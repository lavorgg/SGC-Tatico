<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import { useAuthMock } from '../stores/authMock'

const { estado } = useAuthMock()

const arenas = ref([])
const equipamentos = ref([])
const arenaSelecionada = ref('')
const dataHoraInicio = ref('')
const dataHoraFim = ref('')
const quantidadesEquipamento = ref({})
const carregando = ref(false)
const mensagemErro = ref('')
const mensagemSucesso = ref('')
const ultimaReservaId = ref(null)

onMounted(async () => {
  try {
    const [respArenas, respEquipamentos] = await Promise.all([
      api.get('/arenas/'),
      api.get('/equipamentos/'),
    ])
    arenas.value = respArenas.data
    equipamentos.value = respEquipamentos.data
    for (const eq of equipamentos.value) {
      quantidadesEquipamento.value[eq.id] = 0
    }
  } catch (erro) {
    mensagemErro.value = 'Não foi possível carregar arenas/equipamentos. O backend está rodando?'
    console.error(erro)
  }
})

function montarItensEquipamento() {
  return Object.entries(quantidadesEquipamento.value)
    .filter(([, quantidade]) => quantidade > 0)
    .map(([equipamentoId, quantidade]) => ({
      equipamento: Number(equipamentoId),
      quantidade_alugada: quantidade,
    }))
}

async function criarReserva() {
  mensagemErro.value = ''
  mensagemSucesso.value = ''

  if (!dataHoraInicio.value || !dataHoraFim.value || dataHoraFim.value <= dataHoraInicio.value) {
    mensagemErro.value = 'O horário de fim precisa ser depois do horário de início.'
    return
  }

  carregando.value = true

  try {
    const resposta = await api.post('/reservas/', {
      usuario: estado.usuarioLogado.usuarioId,
      arena: arenaSelecionada.value,
      data_hora_inicio: dataHoraInicio.value,
      data_hora_fim: dataHoraFim.value,
      itens_equipamento: montarItensEquipamento(),
    })
    mensagemSucesso.value = `Reserva #${resposta.data.id} criada com sucesso.`
    ultimaReservaId.value = resposta.data.id
  } catch (erro) {
    mensagemErro.value = erro.response?.data?.detail || 'Erro inesperado ao criar reserva. Confere o console.'
    if (!erro.response) console.error(erro)
  } finally {
    carregando.value = false
  }
}

async function assinarTermo() {
  try {
    const resposta = await api.post(`/reservas/${ultimaReservaId.value}/assinar_termo/`)
    mensagemSucesso.value = `Termo assinado. QR Code: ${resposta.data.qr_code_url}`
  } catch (erro) {
    mensagemErro.value = erro.response?.data?.detail || 'Erro ao assinar termo.'
  }
}
</script>

<template>
  <div class="min-h-screen bg-caatinga-escuro text-caatinga-caqui p-4 max-w-lg mx-auto">
    <h1 class="text-xl font-bold mb-1">Painel do Jogador</h1>
    <p class="text-sm text-caatinga-caqui/70 mb-6">Logado como {{ estado.usuarioLogado?.nome }} (ID {{ estado.usuarioLogado?.usuarioId }})</p>

    <label class="block text-sm mb-1">Arena</label>
    <select v-model="arenaSelecionada" class="w-full mb-4 px-3 py-2 rounded bg-caatinga-verde/20 border border-caatinga-oliva">
      <option value="" disabled>Selecione uma arena</option>
      <option v-for="arena in arenas" :key="arena.id" :value="arena.id">
        {{ arena.nome }} — capacidade {{ arena.capacidade_maxima }} — R$ {{ arena.valor_locacao }}
      </option>
    </select>

    <label class="block text-sm mb-1">Início</label>
    <input v-model="dataHoraInicio" type="datetime-local" class="w-full mb-4 px-3 py-2 rounded bg-caatinga-verde/20 border border-caatinga-oliva" />

    <label class="block text-sm mb-1">Fim</label>
    <input v-model="dataHoraFim" type="datetime-local" class="w-full mb-4 px-3 py-2 rounded bg-caatinga-verde/20 border border-caatinga-oliva" />

    <div v-if="equipamentos.length" class="mb-4">
      <p class="text-sm mb-2">Equipamentos (opcional)</p>
      <div v-for="eq in equipamentos" :key="eq.id" class="flex items-center justify-between mb-2 bg-caatinga-verde/10 px-3 py-2 rounded">
        <span class="text-sm">{{ eq.nome }} <span class="text-caatinga-caqui/60">(estoque: {{ eq.quantidade_estoque }})</span></span>
        <input
          v-model.number="quantidadesEquipamento[eq.id]"
          type="number"
          min="0"
          :max="eq.quantidade_estoque"
          class="w-16 px-2 py-1 rounded bg-caatinga-escuro border border-caatinga-oliva text-center"
        />
      </div>
    </div>

    <button
      @click="criarReserva"
      :disabled="carregando"
      class="w-full py-2 rounded bg-caatinga-terra text-white font-semibold hover:bg-caatinga-oliva transition disabled:opacity-50"
    >
      {{ carregando ? 'Enviando...' : 'Reservar' }}
    </button>

    <p v-if="mensagemErro" class="mt-4 text-red-400 text-sm">{{ mensagemErro }}</p>
    <p v-if="mensagemSucesso" class="mt-4 text-green-400 text-sm">{{ mensagemSucesso }}</p>

    <button
      v-if="ultimaReservaId && !mensagemSucesso.includes('Termo')"
      @click="assinarTermo"
      class="w-full mt-3 py-2 rounded border border-caatinga-oliva text-caatinga-caqui hover:bg-caatinga-oliva/20 transition"
    >
      Assinar termo dessa reserva
    </button>
  </div>
</template>