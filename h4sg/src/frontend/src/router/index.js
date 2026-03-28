import { createRouter, createWebHistory } from 'vue-router'
import BoxView from '../views/BoxView.vue'
import AddBook from '../views/AddBook.vue'
import BookList from '@/views/BookList.vue'
import RemoveBook from '../views/RemoveBook.vue'
import InfoAboutBook from '../views/InfoAboutBook.vue'
import Home from '@/views/Home.vue'
import BoxActions from '@/views/BoxActions.vue'
import Games from '@/views/Games.vue'
import HelpTheBox from '@/views/HelpTheBox.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: Home, meta: { bgClass: 'page-cream' } },

    // Box home — QR code points here: /box/4
    {
      path: '/box/:id',
      name: 'box',
      component: BoxView,
      children: [
        // Actions scoped to a specific box
        { path: '', name: 'boxHome', component: BoxActions, meta: { bgClass: 'page-yellow' } },
        { path: 'add', name: 'add', component: AddBook, meta: { bgClass: 'page-purple' } },
        {
          path: 'borrow',
          name: 'borrow',
          component: RemoveBook,
          meta: { bgClass: 'page-purple' },
        },
        {
          path: 'books',
          name: 'books',
          component: BookList,
          meta: { bgClass: 'page-orange' },
        },
        {
          path: 'info',
          name: 'info',
          component: InfoAboutBook,
          meta: { bgClass: 'page-orange' },
        },
        {
          path: 'games',
          name: 'games',
          component: Games,
          meta: { bgClass: 'page-cream' },
        },
        {
          path: 'help',
          name: 'help',
          component: HelpTheBox,
          meta: { bgClass: 'page-cream' },
        },
      ],
    },

    // Catch-all: unknown routes redirect to /box
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

export default router
