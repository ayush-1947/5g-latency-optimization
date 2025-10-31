class Slice:
    def __init__(self, name, ratio,
                 connected_users, user_share, delay_tolerance, qos_class,
                 bandwidth_guaranteed, bandwidth_max, init_capacity,
                 usage_pattern):
        self.name = name
        self.connected_users = connected_users
        self.user_share = user_share
        self.delay_tolerance = delay_tolerance
        self.qos_class = qos_class
        self.ratio = ratio
        self.bandwidth_guaranteed = bandwidth_guaranteed
        self.bandwidth_max = bandwidth_max
        self.init_capacity = init_capacity
        self.capacity = 0
        self.usage_pattern = usage_pattern
        
        # Enhanced resource allocation parameters
        self.reserved_capacity = 0  # Reserve for high-priority/low-latency traffic
        self.active_clients = []    # List of active clients for dynamic allocation
        self.latency_history = []   # Track historical latency for adaptation
        self.avg_latency = 0        # Current average latency
        self.sla_violations = 0     # Count of SLA violations
    
    def get_consumable_share(self):
        """Calculate how much bandwidth a client can consume"""
        if self.connected_users <= 0:
            return min(self.init_capacity, self.bandwidth_max)
        else:
            # Apply prioritization based on QoS class for low-latency slices
            if self.qos_class <= 2:  # Higher priority (lower number) gets more
                # Prioritize low-latency slices by using a higher weight
                priority_factor = 1.2  # 20% boost for high-priority services
                basic_share = min(self.init_capacity/self.connected_users, self.bandwidth_max)
                return min(basic_share * priority_factor, self.bandwidth_max)
            else:
                # Standard allocation for regular slices
                return min(self.init_capacity/self.connected_users, self.bandwidth_max)

    def is_avaliable(self):
        """Determine if slice can accept new clients"""
        real_cap = min(self.init_capacity, self.bandwidth_max)
        
        # Account for reserved capacity for high-priority traffic
        available_cap = real_cap - self.reserved_capacity
        
        # Check if adding another client would reduce bandwidth below guarantee
        bandwidth_next = available_cap / (self.connected_users + 1)
        if bandwidth_next < self.bandwidth_guaranteed:
            return False
            
        # For low-latency slices (QoS class 1-2), be more conservative
        if self.qos_class <= 2 and self.avg_latency > (0.7 * self.delay_tolerance):
            # If we're already approaching latency limits, be more restrictive
            if self.connected_users >= (real_cap / (self.bandwidth_guaranteed * 1.5)):
                return False
                
        return True

    def update_latency_stats(self, new_latency):
        """Update slice's latency statistics"""
        self.latency_history.append(new_latency)
        
        # Keep history to a reasonable size (last 100 values)
        if len(self.latency_history) > 100:
            self.latency_history.pop(0)
            
        # Update average latency
        if self.latency_history:
            self.avg_latency = sum(self.latency_history) / len(self.latency_history)
            
        # Check for SLA violation
        if new_latency > self.delay_tolerance:
            self.sla_violations += 1
            
        # Adjust reserved capacity based on recent latency trends
        self._adapt_reserved_capacity()

    def _adapt_reserved_capacity(self):
        """Dynamically adjust reserved capacity based on latency trends"""
        if not self.latency_history or len(self.latency_history) < 5:
            return
            
        # Get recent trend (last 5 measurements)
        recent = self.latency_history[-5:]
        recent_avg = sum(recent) / len(recent)
        
        # If recent latency is higher than overall average, increase reservation
        if recent_avg > self.avg_latency and recent_avg > (0.8 * self.delay_tolerance):
            # Reserve additional capacity (up to 10% of total)
            new_reserve = min(self.init_capacity * 0.1, self.reserved_capacity + (self.init_capacity * 0.02))
            self.reserved_capacity = new_reserve
        # If recent latency is lower, we can reduce reservation
        elif recent_avg < self.avg_latency and recent_avg < (0.5 * self.delay_tolerance):
            # Reduce reservation gradually
            self.reserved_capacity = max(0, self.reserved_capacity - (self.init_capacity * 0.01))

    def dynamic_resource_allocation(self, clients):
        """Implement dynamic resource allocation for connected clients"""
        if not clients:
            return
            
        # Store active clients for future reference
        self.active_clients = clients
        
        # Sort clients by urgency/priority
        # Priority factors: time in system, latency sensitivity, QoS class
        prioritized_clients = sorted(clients, key=lambda c: (
            c.env.now - c.request_start_time if hasattr(c, 'request_start_time') else 0,
            self.delay_tolerance,
            self.qos_class
        ), reverse=True)
        
        # Calculate total remaining demand
        total_demand = sum(c.usage_remaining for c in prioritized_clients if hasattr(c, 'usage_remaining'))
        
        # Available capacity minus reserved
        available_capacity = self.capacity.level - self.reserved_capacity
        
        # If we have enough capacity for all, proportionally allocate based on demand
        if total_demand <= available_capacity:
            for client in prioritized_clients:
                if hasattr(client, 'allocated_bandwidth'):
                    client.allocated_bandwidth = client.usage_remaining
        else:
            # Not enough capacity - prioritize allocation
            remaining_capacity = available_capacity
            
            # First pass: ensure minimum guaranteed bandwidth
            for client in prioritized_clients:
                if hasattr(client, 'allocated_bandwidth'):
                    min_alloc = min(self.bandwidth_guaranteed, client.usage_remaining)
                    client.allocated_bandwidth = min_alloc
                    remaining_capacity -= min_alloc
                    
            # Second pass: distribute remaining bandwidth by priority
            if remaining_capacity > 0:
                for client in prioritized_clients:
                    if hasattr(client, 'allocated_bandwidth'):
                        # Calculate priority weight based on QoS and time in system
                        time_factor = min(1.0, (client.env.now - client.request_start_time) / self.delay_tolerance) if hasattr(client, 'request_start_time') else 0.5
                        qos_weight = (5 - self.qos_class) / 5  # QoS classes 1-5, lower is higher priority
                        priority = time_factor * qos_weight
                        
                        # Allocate additional bandwidth based on priority
                        additional = min(
                            remaining_capacity * priority,
                            client.usage_remaining - client.allocated_bandwidth
                        )
                        client.allocated_bandwidth += additional
                        remaining_capacity -= additional
                        
                        if remaining_capacity <= 0:
                            break

    def __str__(self):
        latency_info = f", avg_latency={self.avg_latency:.3f}" if hasattr(self, 'avg_latency') and self.avg_latency > 0 else ""
        return f'{self.name:<10} init={self.init_capacity:<5} cap={self.capacity.level:<5} diff={(self.init_capacity - self.capacity.level):<5}{latency_info}'