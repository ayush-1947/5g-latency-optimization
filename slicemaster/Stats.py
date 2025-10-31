class Stats:
    def __init__(self, env, base_stations, clients, area):
        self.env = env
        self.base_stations = base_stations
        self.clients = clients
        self.area = area

        # Stats
        self.total_connected_users_ratio = []
        self.total_used_bw = []
        self.avg_slice_load_ratio = []
        self.avg_slice_client_count = []
        self.coverage_ratio = []
        self.connect_attempt = []
        self.block_count = []
        self.handover_count = []
        
        # Latency statistics
        self.avg_latency = []
        self.avg_latency_per_slice = {}
        self.max_latency = []
        self.min_latency = []
        self.latency_sla_violations = []
        self.handover_latencies = []
    
    def get_stats(self):
        # Include latency metrics in the returned stats
        if hasattr(self, 'avg_latency') and self.avg_latency:
            return (
                self.total_connected_users_ratio,
                self.total_used_bw,
                self.avg_slice_load_ratio,
                self.avg_slice_client_count,
                self.coverage_ratio,
                self.block_count,
                self.handover_count,
                self.avg_latency,
                self.avg_latency_per_slice,
                self.max_latency,
                self.latency_sla_violations,
            )
        else:
            # Original return values if no latency data
            return (
                self.total_connected_users_ratio,
                self.total_used_bw,
                self.avg_slice_load_ratio,
                self.avg_slice_client_count,
                self.coverage_ratio,
                self.block_count,
                self.handover_count,
            )

    def collect(self):
        yield self.env.timeout(0.25)
        self.connect_attempt.append(0)
        self.block_count.append(0)
        self.handover_count.append(0)
        while True:
            # Calculate ratios from counts
            self.block_count[-1] /= self.connect_attempt[-1] if self.connect_attempt[-1] != 0 else 1
            self.handover_count[-1] /= self.connect_attempt[-1] if self.connect_attempt[-1] != 0 else 1

            # Collect standard metrics
            self.total_connected_users_ratio.append(self.get_total_connected_users_ratio())
            self.total_used_bw.append(self.get_total_used_bw())
            self.avg_slice_load_ratio.append(self.get_avg_slice_load_ratio())
            self.avg_slice_client_count.append(self.get_avg_slice_client_count())
            self.coverage_ratio.append(self.get_coverage_ratio())
            
            # Collect latency metrics
            self.collect_latency_stats()

            # Reset counters for next period
            self.connect_attempt.append(0)
            self.block_count.append(0)
            self.handover_count.append(0)
            
            yield self.env.timeout(1)

    def collect_latency_stats(self):
        """Collect and calculate latency statistics"""
        if not self.clients:
            self.avg_latency.append(0)
            self.max_latency.append(0)
            self.min_latency.append(0)
            self.latency_sla_violations.append(0)
            return
            
        # Per-slice latency tracking
        slice_latencies = {}
        for bs in self.base_stations:
            for i, sl in enumerate(bs.slices):
                slice_name = sl.name
                if slice_name not in slice_latencies:
                    slice_latencies[slice_name] = []
        
        # Calculate overall latency statistics
        all_latencies = []
        sla_violations = 0
        
        for client in self.clients:
            if not hasattr(client, 'latencies') or not client.latencies:
                continue
                
            # Only consider clients in the statistics area
            if not self.is_client_in_coverage(client):
                continue
                
            # Get the latest latency
            latest_latency = client.latencies[-1] if client.latencies else 0
            all_latencies.append(latest_latency)
            
            # Track per-slice latency
            if client.base_station is not None:
                slice_name = client.get_slice().name
                if slice_name in slice_latencies:
                    slice_latencies[slice_name].append(latest_latency)
                    
            # Check for SLA violations
            if client.get_slice() and hasattr(client.get_slice(), 'delay_tolerance'):
                if latest_latency > client.get_slice().delay_tolerance:
                    sla_violations += 1
        
        # Calculate and store overall statistics
        if all_latencies:
            self.avg_latency.append(sum(all_latencies) / len(all_latencies))
            self.max_latency.append(max(all_latencies))
            self.min_latency.append(min(all_latencies))
        else:
            self.avg_latency.append(0)
            self.max_latency.append(0)
            self.min_latency.append(0)
            
        # Calculate SLA violation rate
        total_clients = sum(1 for c in self.clients if self.is_client_in_coverage(c))
        self.latency_sla_violations.append(sla_violations / total_clients if total_clients > 0 else 0)
        
        # Calculate per-slice averages
        for slice_name, latencies in slice_latencies.items():
            if slice_name not in self.avg_latency_per_slice:
                self.avg_latency_per_slice[slice_name] = []
                
            if latencies:
                self.avg_latency_per_slice[slice_name].append(sum(latencies) / len(latencies))
            else:
                self.avg_latency_per_slice[slice_name].append(0)

    def record_latency(self, client, latency):
        """Record individual latency event - can be used for more granular analysis"""
        # This method will be called by clients when they record a new latency
        # Can be extended for more sophisticated analysis
        
        # For now, just track handover latencies separately
        if hasattr(client, 'handover_latencies') and client.handover_latencies:
            if len(self.handover_latencies) <= int(self.env.now):
                # Extend the list if needed
                self.handover_latencies.extend([[] for _ in range(int(self.env.now) - len(self.handover_latencies) + 1)])
            
            # Add the latest handover latency
            self.handover_latencies[int(self.env.now)].append(client.handover_latencies[-1])

    def get_total_connected_users_ratio(self):
        t, cc = 0, 0
        for c in self.clients:
            if self.is_client_in_coverage(c):
                t += c.connected
                cc += 1
        return t/cc if cc != 0 else 0

    def get_total_used_bw(self):
        t = 0
        for bs in self.base_stations:
            for sl in bs.slices:
                t += sl.capacity.capacity - sl.capacity.level
        return t

    def get_avg_slice_load_ratio(self):
        t, c = 0, 0
        for bs in self.base_stations:
            for sl in bs.slices:
                c += sl.capacity.capacity
                t += sl.capacity.capacity - sl.capacity.level
        return t/c if c !=0 else 0

    def get_avg_slice_client_count(self):
        t, c = 0, 0
        for bs in self.base_stations:
            for sl in bs.slices:
                c += 1
                t += sl.connected_users
        return t/c if c !=0 else 0
    
    def get_coverage_ratio(self):
        t, cc = 0, 0
        for c in self.clients:
            if self.is_client_in_coverage(c):
                cc += 1
                if c.base_station is not None and c.base_station.coverage.is_in_coverage(c.x, c.y):
                    t += 1
        return t/cc if cc !=0 else 0

    def get_avg_latency_overall(self):
        """Get the average latency across all time periods"""
        if not self.avg_latency:
            return 0
        return sum(self.avg_latency) / len(self.avg_latency)
    
    def get_avg_latency_by_slice(self):
        """Get the average latency for each slice across all time periods"""
        result = {}
        for slice_name, latencies in self.avg_latency_per_slice.items():
            if latencies:
                result[slice_name] = sum(latencies) / len(latencies)
            else:
                result[slice_name] = 0
        return result
    
    def get_sla_violation_rate(self):
        """Get the average SLA violation rate across all time periods"""
        if not self.latency_sla_violations:
            return 0
        return sum(self.latency_sla_violations) / len(self.latency_sla_violations)

    def incr_connect_attempt(self, client):
        if self.is_client_in_coverage(client):
            self.connect_attempt[-1] += 1

    def incr_block_count(self, client):
        if self.is_client_in_coverage(client):
            self.block_count[-1] += 1

    def incr_handover_count(self, client):
        if self.is_client_in_coverage(client):
            self.handover_count[-1] += 1

    def is_client_in_coverage(self, client):
        xs, ys = self.area
        return True if xs[0] <= client.x <= xs[1] and ys[0] <= client.y <= ys[1] else False