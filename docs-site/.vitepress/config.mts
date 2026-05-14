import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'AI Workflow Orchestrator',
  description: 'Production-grade autonomous agentic workflow management system.',

  srcDir: '../docs',
  srcExclude: ['00-pm/**', '01-plan/**', '02-design/**', '03-analyze/**', '04-report/**'],

  base: '/',

  markdown: {
    mermaid: true,
  },

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Architecture', link: '/architecture' },
      { text: 'Guides', link: '/sop/index' },
      { text: 'API', link: '/api/index' },
    ],

    sidebar: [
      {
        text: 'Overview',
        items: [
          { text: 'Introduction', link: '/' },
          { text: 'Codebase Analysis', link: '/analysis' },
          { text: 'User Personas', link: '/personas/user-personas' },
          { text: 'Jobs-to-be-Done', link: '/jtbd/jobs-to-be-done' },
          { text: 'System Flows', link: '/flows/system-flows' },
        ],
      },
      {
        text: 'Architecture & Technical',
        items: [
          { text: 'System Architecture', link: '/architecture' },
          { text: 'Database Schema', link: '/database' },
          { text: 'Deployment Guide', link: '/deployment' },
          { text: 'Data Flow', link: '/data-flow' },
        ],
      },
      {
        text: 'User Guides (SOP)',
        items: [
          { text: 'Overview', link: '/sop/index' },
          { text: 'Workflow Management', link: '/sop/workflow-management' },
          { text: 'System Observability', link: '/sop/system-observability' },
        ],
      },
      {
        text: 'API Reference',
        items: [
          { text: 'Agent Contracts', link: '/api/index' },
        ],
      },
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/kizabgd/memoriJADA' },
    ],

    search: {
      provider: 'local',
    },

    footer: {
      message: 'Built with DocKit Premium',
      copyright: `© ${new Date().getFullYear()}`,
    },

    outline: {
      level: [2, 3],
    },
  },

  appearance: 'dark',

  head: [
    ['meta', { name: 'theme-color', content: '#22d3ee' }],
    ['meta', { name: 'og:type', content: 'website' }],
  ],

  sitemap: {
    hostname: 'https://memori-jada.pages.dev',
  },
})
