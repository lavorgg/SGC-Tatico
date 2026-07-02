import { reactive } from 'vue'

const estado = reactive({
  usuarioLogado: null,
})

function carregarDoStorage() {
  const salvo = localStorage.getItem('sgc_usuario_mock')
  if (salvo) {
    estado.usuarioLogado = JSON.parse(salvo)
  }
}

function login(usuarioId, nome, tipoPerfil) {
  const usuario = { usuarioId: Number(usuarioId), nome, tipoPerfil }
  estado.usuarioLogado = usuario
  localStorage.setItem('sgc_usuario_mock', JSON.stringify(usuario))
}

function logout() {
  estado.usuarioLogado = null
  localStorage.removeItem('sgc_usuario_mock')
}

carregarDoStorage()

export function useAuthMock() {
  return { estado, login, logout }
}