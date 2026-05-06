import { useState } from 'react'
import './App.css'

const API = 'http://127.0.0.1:8000'

function App() {
  const [gameId, setGameId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [hand, setHand] = useState([])
  const [shownCard, setShownCard] = useState(null)
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  // ---------- helpers ----------
  async function api(path, method = 'GET', body = null) {
    const options = { method, headers: {} }
    if (body) {
      options.headers['Content-Type'] = 'application/json'
      options.body = JSON.stringify(body)
    }
    const res = await fetch(`${API}${path}`, options)
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Erreur API')
    }
    return res.json()
  }

  async function refreshHand(id) {
    const cards = await api(`/games/${id}/hand`)
    setHand(cards)
  }

  async function refreshStatus(id) {
    const s = await api(`/games/${id}/status`)
    setStatus(s)
    return s
  }

  // ---------- actions ----------
  async function createGame() {
    setLoading(true)
    setError(null)
    try {
      const data = await api('/games/', 'POST', { player_name: 'alex', player_id: 0 })
      const id = data.game_id
      setGameId(id)
      await refreshHand(id)
      const card = await api(`/games/${id}/showncard`)
      setShownCard(card)
      await refreshStatus(id)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function placeBid(takes) {
    setError(null)
    try {
      const s = await api(`/games/${gameId}/bid?takes=${takes}`, 'POST')
      setStatus(s)
      await refreshHand(gameId)
      if (s.trump_suit) {
        setShownCard(null)
      }
    } catch (e) {
      setError(e.message)
    }
  }

  async function playCard(card) {
    setError(null)
    try {
      const s = await api(`/games/${gameId}/play`, 'POST', {
        rank: card.rank,
        suit: card.suit
      })
      setStatus(s)
      await refreshHand(gameId)
    } catch (e) {
      setError(e.message)
    }
  }

  function resetGame() {
    setGameId(null)
    setHand([])
    setShownCard(null)
    setStatus(null)
    setError(null)
  }

  // ---------- phases ----------
  const gameOver = status?.game_over === true
  const bidPhase = shownCard !== null
  const playPhase = !bidPhase && status?.trump_suit != null && !gameOver

  // ---------- rendu ----------
  return (
    <div className="table">
      <h1 className="title">Belote Online</h1>

      {error && <p className="error">{error}</p>}

      {/* --- Ecran d'accueil --- */}
      {gameId === null && (
        <div className="center-zone">
          <button className="btn btn-main" onClick={createGame} disabled={loading}>
            {loading ? 'Création...' : 'Nouvelle partie'}
          </button>
        </div>
      )}

      {/* --- Scores --- */}
      {status && (
        <div className="scores">
          <span>Nous : {status.team_ns_points}</span>
          <span>Eux : {status.team_ew_points}</span>
          {status.taker != null && <span>Preneur : joueur {status.taker}</span>}
        </div>
      )}

      {/* --- Phase d'enchères --- */}
      {bidPhase && (
        <div className="center-zone">
          <p className="info">Carte retournée :</p>
          <div className="card card-shown">
            {shownCard.rank}{shownCard.suit}
          </div>
          <div className="bid-buttons">
            <button className="btn btn-take" onClick={() => placeBid(true)}>
              Prendre
            </button>
            <button className="btn btn-pass" onClick={() => placeBid(false)}>
              Passer
            </button>
          </div>
        </div>
      )}

      {/* --- Pli en cours --- */}
      {playPhase && status.cards_played && (
        <div className="center-zone">
          <p className="info">
            Atout : {status.trump_suit} — Au tour du joueur {status.current_player}
          </p>
          <div className="trick">
            {status.cards_played.map((c, i) => (
              <div key={i} className="card card-played">{c.rank}{c.suit}</div>
            ))}
          </div>
        </div>
      )}

      {/* --- Game over --- */}
      {gameOver && (
        <div className="center-zone">
          <h2>Partie terminée !</h2>
          <p>Nous : {status.team_ns_points} — Eux : {status.team_ew_points}</p>
          <p>{status.team_ns_points > status.team_ew_points ? 'Victoire !' : 'Défaite...'}</p>
          <button className="btn btn-main" onClick={resetGame}>
            Rejouer
          </button>
        </div>
      )}

      {/* --- Main du joueur --- */}
      {hand.length > 0 && !gameOver && (
        <div className="hand-zone">
          <div className="hand">
            {hand.map((card, i) => (
              <button
                key={i}
                className={`card card-hand ${playPhase ? 'playable' : ''}`}
                disabled={!playPhase}
                onClick={() => playCard(card)}
              >
                <span className={
                  card.suit === '♥' || card.suit === '♦' ? 'red' : 'black'
                }>
                  {card.rank}{card.suit}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
