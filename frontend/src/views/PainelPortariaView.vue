<script setup>
import axios from 'axios'
import { ref, onMounted, onBeforeUnmount } from 'vue'
import QrScanner from 'qr-scanner'
import QrScannerWorkerPath from 'qr-scanner/qr-scanner-worker.min.js?url'
import api from '../services/api'

QrScanner.WORKER_PATH = QrScannerWorkerPath

const videoElement = ref(null)
let scanner = null

const escaneando = ref(true)
const resultado = ref(null)
const mensagemErro = ref('')

async function processarCodigo(urlDecodificada) {
  scanner.stop()
  escaneando.value = false
  mensagemErro.value = ''
  resultado.value = null

  let caminho
  try {
    caminho = new URL(urlDecodificada).pathname
  } catch {
    mensagemErro.value = 'QR Code não reconhecido.'
    return
  }

  try {
    const resposta = await axios.get(caminho)
    resultado.value = resposta.data
  } catch (erro) {
    if (erro.response && erro.response.data) {
      resultado.value = erro.response.data
    } else {
      mensagemErro.value = 'Não foi possível validar o código. O backend está rodando?'
      console.error(erro)
    }
  }
}

function escanearNovamente() {
  resultado.value = null
  mensagemErro.value = ''
  escaneando.value = true
  scanner.start()
}

onMounted(() => {
  scanner = new QrScanner(
    videoElement.value,
    (resultadoLeitura) => processarCodigo(resultadoLeitura.data),
    { highlightScanRegion: true, highlightCodeOutline: true }
  )
  scanner.start().catch((erro) => {
    mensagemErro.value = 'Não foi possível acessar a câmera. Verifica a permissão no navegador.'
    console.error(erro)
  })
})

onBeforeUnmount(() => {
  scanner?.stop()
  scanner?.destroy()
})
</script>

<template>
  <div class="min-h-screen bg-caatinga-escuro text-caatinga-caqui p-4 max-w-lg mx-auto">
    <h1 class="text-xl font-bold mb-1">Painel da Portaria</h1>
    <p class="text-sm text-caatinga-caqui/70 mb-6">Aponte a câmera para o QR Code do jogador</p>

    <video ref="videoElement" class="w-full rounded border border-caatinga-oliva" v-show="escaneando"></video>

    <p v-if="mensagemErro" class="mt-4 text-red-400 text-sm">{{ mensagemErro }}</p>

    <div
      v-if="resultado"
      class="mt-4 p-4 rounded border"
      :class="resultado.valido ? 'border-green-500 bg-green-500/10' : 'border-red-500 bg-red-500/10'"
    >
      <p class="font-bold text-lg" :class="resultado.valido ? 'text-green-400' : 'text-red-400'">
        {{ resultado.valido ? 'ENTRADA LIBERADA' : 'ENTRADA NEGADA' }}
      </p>

      <template v-if="resultado.valido">
        <p class="text-sm mt-2">Organizador: {{ resultado.organizador }}</p>
        <p class="text-sm">Arena: {{ resultado.arena }}</p>
        <p class="text-sm">Horário: {{ resultado.data_hora_inicio }} até {{ resultado.data_hora_fim }}</p>
      </template>
      <p v-else class="text-sm mt-2">{{ resultado.detail }}</p>

      <button
        @click="escanearNovamente"
        class="w-full mt-4 py-2 rounded bg-caatinga-terra text-white font-semibold hover:bg-caatinga-oliva transition"
      >
        Escanear próximo
      </button>
    </div>
  </div>
</template>