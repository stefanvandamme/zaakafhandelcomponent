export interface Tab {
  component: string;
  label: string;
  endpoint: string;
}

const tabs: Tab[] = [
  {
    component: 'zaken',
    label: 'In behandeling',
    endpoint: '/api/workstack/cases'
  },
  {
    component: 'tasks',
    label: 'Taken',
    endpoint: '/api/workstack/user-tasks'
  },
  {
    component: 'activities',
    label: 'Zaakactiviteiten',
    endpoint: '/api/workstack/activities'
  },
  {
    component: 'access-request',
    label: 'Toegangsverzoeken',
    endpoint: '/api/workstack/access-requests'
  },
];

export { tabs }
