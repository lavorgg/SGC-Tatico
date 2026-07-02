import { createRouter, createWebHistory } from 'vue-router'
import { useAuthMock } from '../stores/authMock'
import LoginView from '../views/LoginView.vue'
import PainelJogadorView from '../views/PainelJogadorView.vue'
import PainelPortariaView from '../views/PainelPortariaView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: LoginView },
  {
    path: '/jogador',
    name: 'jogador',
    component: PainelJogadorView,
    meta: { requerLogin: true, perfisPermitidos: ['JOGADOR', 'ADMIN'] },
  },
  {
    path: '/portaria',
    name: 'portaria',
    component: PainelPortariaView,
    meta: { requerLogin: true, perfisPermitidos: ['OPERADOR', 'ADMIN'] },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const { estado } = useAuthMock()

  if (to.meta.requerLogin && !estado.usuarioLogado) {
    return { name: 'login' }
  }

  if (to.meta.perfisPermitidos && !to.meta.perfisPermitidos.includes(estado.usuarioLogado?.tipoPerfil)) {
    return { name: 'login' }
  }
})

export default router