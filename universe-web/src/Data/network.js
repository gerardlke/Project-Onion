export const nodes = [
  {
    id: 1,
    position: [-3, 1, 0],
    color: '#4f46e5',
    label: 'Server Cluster A',
    info: 'Status: Operational | Load: 42%',
  },
  {
    id: 2,
    position: [2, 2, -2],
    color: '#06b6d4',
    label: 'Database B',
    info: 'Status: Syncing | Delay: 12ms',
  },
  {
    id: 3,
    position: [1, -2, 1],
    color: '#10b981',
    label: 'Gateway C',
    info: 'Status: Active | Traffic: High',
  },
];

export const links = [
  [1, 2],
  [2, 3],
  [3, 1],
];
