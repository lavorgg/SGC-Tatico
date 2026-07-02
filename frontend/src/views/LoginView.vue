<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthMock } from '../stores/authMock'

const router = useRouter()
const { login } = useAuthMock()

const nome = ref('')
const tipoPerfil = ref('JOGADOR')

function entrar() {
  if (!nome.value.trim()) return
  login(nome.value.trim(), tipoPerfil.value)
  router.push(tipoPerfil.value === 'OPERADOR' ? '/portaria' : '/jogador')
}
</script>

<template>
  <div class="min-h-screen bg-caatinga-escuro flex items-center justify-center px-4">
    <div class="w-full max-w-sm bg-caatinga-verde/20 border border-caatinga-oliva rounded-lg p-6">
      <h1 class="text-2xl font-bold text-caatinga-caqui mb-1">SGC-Tático</h1>
      <p class="text-sm text-caatinga-caqui/70 mb-6">Login temporário — sem senha, JWT pendente</p>

      <label class="block text-sm text-caatinga-caqui mb-1">Nome</label>
      <input
        v-model="nome"
        type="text"
        placeholder="Seu nome"
        class="w-full mb-4 px-3 py-2 rounded bg-caatinga-escuro border border-caatinga-oliva text-caatinga-caqui focus:outline-none focus:border-caatinga-terra"
      />

      <label class="block text-sm text-caatinga-caqui mb-1">Perfil</label>
      <select
        v-model="tipoPerfil"
        class="w-full mb-6 px-3 py-2 rounded bg-caatinga-escuro border border-caatinga-oliva text-caatinga-caqui"
      >
        <option value="JOGADOR">Jogador</option>
        <option value="OPERADOR">Operador</option>
        <option value="ADMIN">Administrador</option>
      </select>

      <button
        @click="entrar"
        class="w-full py-2 rounded bg-caatinga-terra text-white font-semibold hover:bg-caatinga-oliva transition"
      >
        Entrar
      </button>
    </div>
  </div>
</template>