import math
import os
import random
import sys

import simpy
import yaml

from .BaseStation import BaseStation
from .Client import Client
from .Coverage import Coverage
from .Distributor import Distributor
from .Graph import Graph
from .Slice import Slice
from .Stats import Stats

from .utils import KDTree


def get_dist(d):
    return {
        'randrange': random.randrange, # start, stop, step
        'randint': random.randint, # a, b
        'random': random.random,
        'uniform': random, # a, b
        'triangular': random.triangular, # low, high, mode
        'beta': random.betavariate, # alpha, beta
        'expo': random.expovariate, # lambda
        'gamma': random.gammavariate, # alpha, beta
        'gauss': random.gauss, # mu, sigma
        'lognorm': random.lognormvariate, # mu, sigma
        'normal': random.normalvariate, # mu, sigma
        'vonmises': random.vonmisesvariate, # mu, kappa
        'pareto': random.paretovariate, # alpha
        'weibull': random.weibullvariate # alpha, beta
    }.get(d)


def get_random_mobility_pattern(vals, mobility_patterns):
    i = 0
    r = random.random()

    while vals[i] < r:
        i += 1

    return mobility_patterns[i]


def get_random_slice_index(vals):
    i = 0
    r = random.random()

    while vals[i] < r:
        i += 1
    return i


def dynamic_resource_allocation(env, slices, clients):
    """Process for dynamic resource allocation"""
    while True:
        # Group clients by slice
        clients_by_slice = {}
        for client in clients:
            if client.base_station is None or not client.connected:
                continue
                
            slice_obj = client.get_slice()
            if slice_obj:
                slice_name = slice_obj.name
                if slice_name not in clients_by_slice:
                    clients_by_slice[slice_name] = []
                clients_by_slice[slice_name].append(client)
        
        # Apply dynamic allocation for each slice
        for base_station in base_stations:
            for slice_obj in base_station.slices:
                if hasattr(slice_obj, 'dynamic_resource_allocation'):
                    slice_clients = clients_by_slice.get(slice_obj.name, [])
                    # Filter to clients connected to this base station
                    bs_clients = [c for c in slice_clients if c.base_station == base_station]
                    if bs_clients:
                        slice_obj.dynamic_resource_allocation(bs_clients)
        
        # Run allocation every 0.5 time units
        yield env.timeout(0.5)


if len(sys.argv) != 2:
    print('Please type an input file.')
    print('python -m slicemaster <input-file>')
    exit(1)

# Read YAML file
CONF_FILENAME = os.path.join(os.path.dirname(__file__), sys.argv[1])
try:
    with open(CONF_FILENAME, 'r') as stream:
        data = yaml.load(stream, Loader=yaml.FullLoader)
except FileNotFoundError:
    print('File Not Found:', CONF_FILENAME)
    exit(0)

random.seed()
env = simpy.Environment()

SETTINGS = data['settings']
SLICES_INFO = data['slices']
NUM_CLIENTS = SETTINGS['num_clients']
MOBILITY_PATTERNS = data['mobility_patterns']
BASE_STATIONS = data['base_stations']
CLIENTS = data['clients']

# Check for latency-specific settings
LATENCY_TRACKING = SETTINGS.get('latency_tracking', True)  # Enable by default
DYNAMIC_ALLOCATION = SETTINGS.get('dynamic_allocation', True)  # Enable by default

if SETTINGS['logging']:
    sys.stdout = open(SETTINGS['log_file'],'wt')
else:
    sys.stdout = open(os.devnull, 'w')

collected, slice_weights = 0, []
for __, s in SLICES_INFO.items():
    collected += s['client_weight']
    slice_weights.append(collected)

collected, mb_weights = 0, []
for __, mb in MOBILITY_PATTERNS.items():
    collected += mb['client_weight']
    mb_weights.append(collected)

mobility_patterns = []
for name, mb in MOBILITY_PATTERNS.items():
    mobility_pattern = Distributor(name, get_dist(mb['distribution']), *mb['params'])
    mobility_patterns.append(mobility_pattern)

usage_patterns = {}
for name, s in SLICES_INFO.items():
    usage_patterns[name] = Distributor(name, get_dist(s['usage_pattern']['distribution']), *s['usage_pattern']['params'])

base_stations = []
i = 0
for b in BASE_STATIONS:
    slices = []
    ratios = b['ratios']
    capacity = b['capacity_bandwidth']
    for name, s in SLICES_INFO.items():
        s_cap = capacity * ratios[name]
        # Create slice with latency awareness
        s = Slice(name, ratios[name], 0, s['client_weight'],
                  s['delay_tolerance'],
                  s['qos_class'], s['bandwidth_guaranteed'],
                  s['bandwidth_max'], s_cap, usage_patterns[name])
        s.capacity = simpy.Container(env, init=s_cap, capacity=s_cap)
        slices.append(s)
    base_station = BaseStation(i, Coverage((b['x'], b['y']), b['coverage']), capacity, slices)
    base_stations.append(base_station)
    i += 1

ufp = CLIENTS['usage_frequency']
usage_freq_pattern = Distributor(f'ufp', get_dist(ufp['distribution']), *ufp['params'], divide_scale=ufp['divide_scale'])

x_vals = SETTINGS['statistics_params']['x']
y_vals = SETTINGS['statistics_params']['y']
stats = Stats(env, base_stations, None, ((x_vals['min'], x_vals['max']), (y_vals['min'], y_vals['max'])))

clients = []
for i in range(NUM_CLIENTS):
    loc_x = CLIENTS['location']['x']
    loc_y = CLIENTS['location']['y']
    location_x = get_dist(loc_x['distribution'])(*loc_x['params'])
    location_y = get_dist(loc_y['distribution'])(*loc_y['params'])

    mobility_pattern = get_random_mobility_pattern(mb_weights, mobility_patterns)

    connected_slice_index = get_random_slice_index(slice_weights)
    c = Client(i, env, location_x, location_y,
               mobility_pattern, usage_freq_pattern.generate_scaled(), connected_slice_index, stats)
    clients.append(c)

KDTree.limit = SETTINGS['limit_closest_base_stations']
KDTree.run(clients, base_stations, 0)

stats.clients = clients
env.process(stats.collect())

# Start dynamic resource allocation if enabled
if DYNAMIC_ALLOCATION:
    env.process(dynamic_resource_allocation(env, slices, clients))

env.run(until=int(SETTINGS['simulation_time']))

# Print client statistics with latency information
for client in clients:
    print(client)
    print(f'\tTotal connected time: {client.total_connected_time:>5}')
    print(f'\tTotal unconnected time: {client.total_unconnected_time:>5}')
    print(f'\tTotal request count: {client.total_request_count:>5}')
    print(f'\tTotal consume time: {client.total_consume_time:>5}')
    print(f'\tTotal usage: {client.total_usage:>5}')
    
    # Print latency statistics if available
    if hasattr(client, 'latencies') and client.latencies:
        print(f'\tAverage latency: {client.avg_latency:.3f}')
        print(f'\tMinimum latency: {client.min_latency if client.min_latency != float("inf") else 0:.3f}')
        print(f'\tMaximum latency: {client.max_latency:.3f}')
        print(f'\tHandover count: {client.handover_count}')
    print()

# Print summary statistics
print(stats.get_stats())

# Generate latency analysis report
if LATENCY_TRACKING:
    print("\nLATENCY ANALYSIS")
    print("-" * 50)
    
    # Overall statistics
    if hasattr(stats, 'get_avg_latency_overall'):
        print(f"Overall average latency: {stats.get_avg_latency_overall():.3f}")
    
    # Per-slice statistics
    if hasattr(stats, 'get_avg_latency_by_slice'):
        print("\nAverage latency by slice:")
        for slice_name, avg_latency in stats.get_avg_latency_by_slice().items():
            print(f"  {slice_name}: {avg_latency:.3f}")
    
    # SLA violations
    if hasattr(stats, 'get_sla_violation_rate'):
        print(f"\nSLA violation rate: {stats.get_sla_violation_rate():.3f}")
    
    print("-" * 50)

# Plotting with enhanced latency visualization
if SETTINGS['plotting_params']['plotting']:
    xlim_left = int(SETTINGS['simulation_time'] * SETTINGS['statistics_params']['warmup_ratio'])
    xlim_right = int(SETTINGS['simulation_time'] * (1 - SETTINGS['statistics_params']['cooldown_ratio'])) + 1
    
    graph = Graph(base_stations, clients, (xlim_left, xlim_right),
                  ((x_vals['min'], x_vals['max']), (y_vals['min'], y_vals['max'])),
                  output_dpi=SETTINGS['plotting_params']['plot_file_dpi'],
                  scatter_size=SETTINGS['plotting_params']['scatter_size'],
                  output_filename=SETTINGS['plotting_params']['plot_file'])
                  
    # Get all stats including latency metrics
    all_stats = stats.get_stats()
    graph.draw_all(*all_stats)
    
    if SETTINGS['plotting_params']['plot_save']:
        graph.save_fig()
    if SETTINGS['plotting_params']['plot_show']:
        graph.show_plot()

sys.stdout = sys.__stdout__
print(f'Simulation completed successfully. {"Output saved to: " + SETTINGS["log_file"] if SETTINGS["logging"] else ""}')