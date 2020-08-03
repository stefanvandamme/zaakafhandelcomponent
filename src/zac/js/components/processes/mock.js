const PROCESS_INSTANCES = [
    {
        id: 'proces:1:bc02fd33-a441-4c69-b1db-73c3a475c16b',
        definitionId: 'proces:1',
        title: 'Proces 1',
        subProcesses: [
            {
                id: 'proces:3:629c8519-6e6c-4371-9de7-2110db95ea3b',
                definitionId: 'proces:3',
                title: 'Sub 1',
                subProcesses: [],
                messages: [],
                userTasks: [
                    {
                        id: 'proces:3:task:1',
                        executeUrl: '/core/zaken/:org/:identificatie/proces:3:task:1/',
                        name: 'Adviseren',
                        created: '2020-07-30T15:03:21Z',
                        assignee: {username: 'johndoe', firstName: '', lastName: ''},
                        hasForm: true,
                    }
                ]
            },
            {
                id: 'proces:4:8fa100a1-e659-41f0-8783-6266a0384ef1',
                definitionId: 'proces:4',
                title: 'Sub 2',
                subProcesses: [
                    {
                        id: 'proces:5:d5268a95-ff3c-4e19-8782-67000259f150',
                        definitionId: 'proces:5',
                        title: 'Sub 3',
                        subProcesses: [],
                        messages: [],
                        userTasks: [
                            {
                                id: 'proces:35task:1',
                                executeUrl: '/core/zaken/:org/:identificatie/proces:5:task:1/',
                                name: 'Beoordelen',
                                created: '2020-07-30T15:03:21Z',
                                assignee: {username: 'johndoe', firstName: '', lastName: ''},
                                hasForm: true,
                            },
                            {
                                id: 'proces:5:task:2',
                                executeUrl: '/core/zaken/:org/:identificatie/proces:5:task:2/',
                                name: 'Debugging',
                                created: '2020-07-30T15:03:21Z',
                                assignee: null,
                                hasForm: true,
                            }
                        ]
                    }
                ],
                messages: [],
                userTasks: [],
            }
        ],
        messages: ['Annuleer behandeling', 'Advies vragen'],
        userTasks: [
            {
                id: 'proces:1:task:1',
                executeUrl: '/core/zaken/:org/:identificatie/proces:1:task:1/',
                name: 'Bepalen resultaat',
                created: '2020-07-30T15:03:21Z',
                assignee: {username: 'sergei', firstName: 'Sergei', lastName: 'Maertens'},
                hasForm: true,
            },
            {
                id: 'proces:1:task:2',
                executeUrl: '/core/zaken/:org/:identificatie/proces:1:task:2/',
                name: 'Adviesvraag configureren',
                created: '2020-07-30T18:05:59Z',
                assignee: null,
                hasForm: true,
            }
        ]
    }

];


export { PROCESS_INSTANCES };
