import operator
import random

from .utils import distance, KDTree


class Client:
    def __init__(self, pk, env, x, y, mobility_pattern,
                 usage_freq,
                 subscribed_slice_index, stat_collector,
                 base_station=None):
        self.pk = pk
        self.env = env
        self.x = x
        self.y = y
        self.mobility_pattern = mobility_pattern
        self.usage_freq = usage_freq
        self.base_station = base_station
        self.stat_collector = stat_collector
        self.subscribed_slice_index = subscribed_slice_index
        self.usage_remaining = 0
        self.last_usage = 0
        self.closest_base_stations = []
        self.connected = False

        # Stats
        self.total_connected_time = 0
        self.total_unconnected_time = 0
        self.total_request_count = 0
        self.total_consume_time = 0
        self.total_usage = 0
        
        # Latency tracking
        self.request_start_time = 0
        self.latencies = []
        self.avg_latency = 0
        self.last_latency = 0
        self.max_latency = 0
        self.min_latency = float('inf')
        
        # Handover stats
        self.handover_count = 0
        self.handover_latencies = []
        
        self.action = env.process(self.iter())

    def iter(self):
        '''
        There are four steps in a cycle:
            1- .00: Lock
            2- .25: Stats
            3- .50: Release
            4- .75: Move
        '''

        # .00: Lock
        if self.base_station is not None:
            if self.usage_remaining > 0:
                if self.connected:
                    self.start_consume()
                else:
                    # Track time when connection attempt starts
                    self.request_start_time = self.env.now
                    self.connect()
            else:
                if self.connected:
                    self.disconnect()
                else:
                    self.generate_usage_and_connect()
        
        yield self.env.timeout(0.25)

        # .25: Stats
        if self.connected:
            self.total_connected_time += 0.25
        else:
            self.total_unconnected_time += 0.25
        
        yield self.env.timeout(0.25)
        
        # .50: Release
        # Base station check skipped as it's already implied by self.connected
        if self.connected and self.last_usage > 0:
            self.release_consume()
            if self.usage_remaining <= 0:
                self.disconnect()

        yield self.env.timeout(0.25)
        
        # .75: Move
        # Move the client
        x, y = self.mobility_pattern.generate_movement()
        self.x += x
        self.y += y

        if self.base_station is not None:
            if not self.base_station.coverage.is_in_coverage(self.x, self.y):
                # Record time before handover for latency tracking
                handover_start_time = self.env.now
                old_bs = self.base_station
                
                self.disconnect()
                self.assign_closest_base_station(exclude=[old_bs.pk])
                
                # Calculate handover latency
                if self.base_station is not None:
                    handover_latency = self.env.now - handover_start_time
                    self.handover_latencies.append(handover_latency)
                    self.handover_count += 1
        else:
            self.assign_closest_base_station()
        
        yield self.env.timeout(0.25)
        
        yield self.env.process(self.iter())

    def get_slice(self):
        if self.base_station is None:
            return None
        return self.base_station.slices[self.subscribed_slice_index]
    
    def generate_usage_and_connect(self):
        if self.usage_freq < random.random() and self.get_slice() is not None:
            # Generate a new usage
            self.usage_remaining = self.get_slice().usage_pattern.generate()
            self.total_request_count += 1
            # Record start time for latency tracking
            self.request_start_time = self.env.now
            self.connect()
            print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] requests {self.usage_remaining} usage.')

    def connect(self):
        s = self.get_slice()
        if self.connected:
            return
        # increment connect attempt
        self.stat_collector.incr_connect_attempt(self)
        if s.is_avaliable():
            s.connected_users += 1
            self.connected = True
            # Calculate connection latency
            connection_latency = self.env.now - self.request_start_time
            self.latencies.append(connection_latency)
            # Update latency statistics
            self._update_latency_stats(connection_latency)
            
            print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] connected to slice={self.get_slice()} @ {self.base_station} (latency: {connection_latency:.3f})')
            return True
        else:
            # Track handover attempt for enhanced resource allocation
            handover_start = self.env.now
            old_bs = self.base_station
            
            self.assign_closest_base_station(exclude=[self.base_station.pk])
            
            if self.base_station is not None and self.base_station != old_bs:
                # Calculate handover latency
                handover_latency = self.env.now - handover_start
                self.handover_latencies.append(handover_latency)
                
            if self.base_station is not None and self.get_slice().is_avaliable():
                # handover
                self.stat_collector.incr_handover_count(self)
                self.handover_count += 1
            elif self.base_station is not None:
                # block
                self.stat_collector.incr_block_count(self)
            else:
                pass # uncovered
            print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] connection refused to slice={self.get_slice()} @ {self.base_station}')
            return False

    def disconnect(self):
        if self.connected == False:
            print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] is already disconnected from slice={self.get_slice()} @ {self.base_station}')
        else:
            slice = self.get_slice()
            slice.connected_users -= 1
            self.connected = False
            print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] disconnected from slice={self.get_slice()} @ {self.base_station}')
        return not self.connected

    def start_consume(self):
        s = self.get_slice()
        # Record start time for service latency tracking
        self.request_start_time = self.env.now
        
        # Get QoS-aware allocation based on slice
        amount = min(s.get_consumable_share(), self.usage_remaining)
        
        # Check for priority based on latency requirements
        if hasattr(s, 'delay_tolerance') and s.delay_tolerance < 10:
            # Prioritize low-latency traffic
            # This could be enhanced with more sophisticated algorithms
            amount = min(amount * 1.2, self.usage_remaining)  # Try to allocate 20% more for low-latency
        
        # Allocate resource and consume ongoing usage with given bandwidth
        s.capacity.get(amount)
        print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] gets {amount} usage.')
        self.last_usage = amount

    def release_consume(self):
        s = self.get_slice()
        # Put the resource back
        if self.last_usage > 0: # note: s.capacity.put cannot take 0
            s.capacity.put(self.last_usage)
            
            # Calculate service latency
            service_latency = self.env.now - self.request_start_time
            self.latencies.append(service_latency)
            
            # Update latency statistics
            self._update_latency_stats(service_latency)
            
            print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] puts back {self.last_usage} usage with latency {service_latency:.3f}.')
            
            # Check if latency exceeds slice's tolerance
            if hasattr(s, 'delay_tolerance') and service_latency > s.delay_tolerance:
                print(f'[{int(self.env.now)}] WARNING: Client_{self.pk} experienced latency ({service_latency:.3f}) exceeding tolerance ({s.delay_tolerance})!')
                # Could trigger adaptive resource allocation here
            
            self.total_consume_time += 1
            self.total_usage += self.last_usage
            self.usage_remaining -= self.last_usage
            self.last_usage = 0

    def _update_latency_stats(self, new_latency):
        """Update latency statistics with a new measurement"""
        self.last_latency = new_latency
        if new_latency > self.max_latency:
            self.max_latency = new_latency
        if new_latency < self.min_latency:
            self.min_latency = new_latency
        self.avg_latency = sum(self.latencies) / len(self.latencies)
        
        # Also update the stat collector if needed
        if hasattr(self.stat_collector, 'record_latency'):
            self.stat_collector.record_latency(self, new_latency)

    # Check closest base_stations of a client and assign the closest non-excluded avaliable base_station to the client.
    def assign_closest_base_station(self, exclude=None):
        updated_list = []
        for d, b in self.closest_base_stations:
            if exclude is not None and b.pk in exclude:
                continue
            d = distance((self.x, self.y), (b.coverage.center[0], b.coverage.center[1]))
            
            # Enhanced base station selection considering load factor
            # This helps with latency by avoiding congested base stations
            slice_load = 0
            if hasattr(b, 'slices') and len(b.slices) > self.subscribed_slice_index:
                target_slice = b.slices[self.subscribed_slice_index]
                # Calculate load as percentage of capacity used
                if hasattr(target_slice, 'capacity') and hasattr(target_slice.capacity, 'level'):
                    slice_load = 1 - (target_slice.capacity.level / target_slice.capacity.capacity)
            
            # Weighted score: distance + load factor
            # Lower score is better (closer + less loaded)
            score = d * (1 + slice_load)
            updated_list.append((score, d, b))
            
        # Sort by the combined score instead of just distance
        updated_list.sort(key=operator.itemgetter(0))
        
        for score, d, b in updated_list:
            if d <= b.coverage.radius:
                self.base_station = b
                print(f'[{int(self.env.now)}] Client_{self.pk} freshly assigned to {self.base_station} (score: {score:.3f})')
                return
                
        if KDTree.last_run_time is not int(self.env.now):
            KDTree.run(self.stat_collector.clients, self.stat_collector.base_stations, int(self.env.now), assign=False)
        self.base_station = None

    def get_qos_metrics(self):
        """Return QoS metrics for this client"""
        return {
            'avg_latency': self.avg_latency,
            'max_latency': self.max_latency,
            'min_latency': self.min_latency if self.min_latency != float('inf') else 0,
            'handover_count': self.handover_count,
            'avg_handover_latency': sum(self.handover_latencies) / len(self.handover_latencies) if self.handover_latencies else 0,
            'connected_ratio': self.total_connected_time / (self.total_connected_time + self.total_unconnected_time) if (self.total_connected_time + self.total_unconnected_time) > 0 else 0
        }

    def __str__(self):
        latency_info = f", avg latency: {self.avg_latency:.3f}" if self.latencies else ""
        return f'Client_{self.pk} [{self.x:<5}, {self.y:>5}] connected to: slice={self.get_slice()} @ {self.base_station}\t with mobility pattern of {self.mobility_pattern}{latency_info}'