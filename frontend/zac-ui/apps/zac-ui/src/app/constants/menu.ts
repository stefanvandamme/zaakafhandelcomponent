import { MenuItem } from '@gu/models';
import {isTestEnvironment} from "@gu/utils";

const menuItems: MenuItem[] = [
  {
    icon: 'inventory',
    label: 'Werkvoorraad',
    to: '/',
  },
  {
    icon: 'dashboard',
    label: 'Dashboard',
    to: '/dashboard',
  },
  {
    icon: 'search',
    label: 'Zoeken',
    to: '/zoeken',
  },
  {
    icon: 'feed',
    label: 'Formulieren',
    to: '/formulieren',
  },
  {
    icon: 'summarize',
    label: 'Rapportages',
    to: '/rapportages',
  },
];

const bottomMenuItems: MenuItem[] = [
  // {
  //   icon: 'login',
  //   label: 'Inloggen',
  //   to: '/accounts/login/?next=/ui/',
  //   external: true
  // },
  {
    icon: 'link',
    label: 'Alfresco',
    to: isTestEnvironment() ? 'https://alfresco-tezza.cg-intern.ont.utrecht.nl/' : 'https://alfresco-tezza.cg-intern.acc.utrecht.nl/',
    external: true,
  },
  {
    icon: 'manage_accounts',
    label: 'Autorisaties',
    to: '/autorisaties',
    // roles: [UserRole.Admin],
  },
  {
    icon: 'admin_panel_settings',
    label: 'Admin',
    to: '/admin',
    external: true,
    // roles: [UserRole.Admin],
  },
];
export { MenuItem, menuItems, bottomMenuItems };
