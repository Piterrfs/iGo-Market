'use client'

import { useState, useEffect } from 'react'
import { Search, TrendingDown, Store, Download, RefreshCw } from 'lucide-react'
import axios from 'axios'

interface Produto {
  produto: string
  marca: string
  quantidade: string
  preco: number
  mercado: string
  data_extracao?: string
}

interface Comparacao {
  produto: string
  marca: string
  quantidade: string
  menor_preco: number
  mercado_menor_preco: string
  todos_precos: Array<{ mercado: string; preco: number }>
  economia: number
  percentual_economia: number
  is_isca: boolean
  mercados_comparados: string[]
}

export default function Home() {
  const [busca, setBusca] = useState('')
  const [resultados, setResultados] = useState<Comparacao[]>([])
  const [carregando, setCarregando] = useState(false)
  const [estatisticas, setEstatisticas] = useState<any>(null)
  const [atualizando, setAtualizando] = useState(false)

  useEffect(() => {
    carregarEstatisticas()
  }, [])

  const carregarEstatisticas = async () => {
    try {
      const response = await axios.get('/api/estatisticas')
      setEstatisticas(response.data)
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error)
    }
  }

  const buscarProdutos = async () => {
    if (!busca.trim()) return

    setCarregando(true)
    try {
      const response = await axios.get('/api/comparar', {
        params: { produto: busca }
      })
      setResultados(response.data.resultados || [])
    } catch (error) {
      console.error('Erro ao buscar:', error)
      alert('Erro ao buscar produtos. Verifique se o backend está rodando.')
    } finally {
      setCarregando(false)
    }
  }

  const executarScraping = async () => {
    setAtualizando(true)
    try {
      const response = await axios.post('/api/scrape')
      alert(response.data.message)
      carregarEstatisticas()
      if (busca) buscarProdutos()
    } catch (error) {
      console.error('Erro ao atualizar:', error)
      alert('Erro ao atualizar dados.')
    } finally {
      setAtualizando(false)
    }
  }

  const baixarPlanilha = async () => {
    try {
      const response = await axios.get('/api/planilha', {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `comparacao_precos_${new Date().toISOString().split('T')[0]}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Erro ao baixar planilha:', error)
      alert('Erro ao gerar planilha.')
    }
  }

  const formatarPreco = (preco: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(preco)
  }

  return (
    <main className="min-h-screen pb-8">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-2xl md:text-3xl font-bold mb-2">
            🛒 iGo Market
          </h1>
          <p className="text-blue-100 text-sm md:text-base">
            Compare preços em supermercados do Rio de Janeiro
          </p>
        </div>
      </header>

      {/* Estatísticas */}
      {estatisticas && (
        <div className="container mx-auto px-4 mt-4">
          <div className="bg-white rounded-lg shadow p-4 mb-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-gray-600 text-xs">Produtos</p>
                <p className="text-2xl font-bold text-blue-600">{estatisticas.total_produtos}</p>
              </div>
              <div>
                <p className="text-gray-600 text-xs">Mercados</p>
                <p className="text-2xl font-bold text-blue-600">{estatisticas.total_mercados}</p>
              </div>
              <div>
                <p className="text-gray-600 text-xs">Preço Médio</p>
                <p className="text-2xl font-bold text-blue-600">
                  {formatarPreco(estatisticas.preco_medio || 0)}
                </p>
              </div>
              <div>
                <p className="text-gray-600 text-xs">Última Atualização</p>
                <p className="text-sm font-semibold text-gray-700">
                  {estatisticas.data_atualizacao || 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Busca */}
      <div className="container mx-auto px-4 mt-4">
        <div className="bg-white rounded-lg shadow-lg p-4">
          <div className="flex flex-col md:flex-row gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Buscar produto (ex: arroz, leite, sabão)..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && buscarProdutos()}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              onClick={buscarProdutos}
              disabled={carregando}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {carregando ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Buscando...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Buscar
                </>
              )}
            </button>
          </div>

          {/* Ações */}
          <div className="flex flex-wrap gap-2 mt-4">
            <button
              onClick={executarScraping}
              disabled={atualizando}
              className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${atualizando ? 'animate-spin' : ''}`} />
              {atualizando ? 'Atualizando...' : 'Atualizar Dados'}
            </button>
            <button
              onClick={baixarPlanilha}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-purple-700 flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Baixar Planilha
            </button>
          </div>
        </div>
      </div>

      {/* Resultados */}
      {resultados.length > 0 && (
        <div className="container mx-auto px-4 mt-6">
          <h2 className="text-xl font-bold mb-4 text-gray-800">
            Resultados ({resultados.length})
          </h2>
          <div className="space-y-4">
            {resultados.map((item, index) => (
              <div
                key={index}
                className="bg-white rounded-lg shadow-lg p-4 border-l-4 border-blue-500"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-bold text-gray-800">
                      {item.produto}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {item.marca} • {item.quantidade}
                    </p>
                  </div>
                  <div className="mt-2 md:mt-0 text-right">
                    <p className="text-2xl font-bold text-green-600">
                      {formatarPreco(item.menor_preco)}
                    </p>
                    <p className="text-sm text-gray-600 flex items-center justify-end gap-1">
                      <Store className="w-4 h-4" />
                      {item.mercado_menor_preco}
                    </p>
                  </div>
                </div>

                {item.economia > 0 && (
                  <div className="bg-green-50 rounded p-2 mb-3">
                    <p className="text-sm text-green-700 flex items-center gap-1">
                      <TrendingDown className="w-4 h-4" />
                      Economia de {formatarPreco(item.economia)} ({item.percentual_economia.toFixed(1)}%)
                    </p>
                  </div>
                )}

                {item.is_isca && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded p-2 mb-3">
                    <p className="text-xs text-yellow-800 font-semibold">
                      ⚠️ OPORTUNIDADE: Desconto acima de 30% - Considere estocar!
                    </p>
                  </div>
                )}

                {/* Comparação com outros mercados */}
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-600 mb-2">Comparação em outros mercados:</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {item.todos_precos.map((preco, idx) => (
                      <div
                        key={idx}
                        className={`text-xs p-2 rounded ${
                          preco.mercado === item.mercado_menor_preco
                            ? 'bg-green-100 text-green-800 font-semibold'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        <p className="font-semibold">{preco.mercado}</p>
                        <p>{formatarPreco(preco.preco)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {resultados.length === 0 && busca && !carregando && (
        <div className="container mx-auto px-4 mt-6">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
            <p className="text-yellow-800">
              Nenhum resultado encontrado. Tente atualizar os dados primeiro.
            </p>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="container mx-auto px-4 mt-8 text-center text-gray-600 text-sm">
        <p>iGo Market © 2026 - Comparador de Preços RJ</p>
      </footer>
    </main>
  )
}


