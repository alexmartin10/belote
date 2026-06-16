import { useState } from 'react'
import './App.css'

const API = import.meta.env.VITE_API_URL ?? ''
const ALL_SUITS = ['♥', '♦', '♠', '♣']

// Mapping index joueur → position sur la table (humain au sud)
const POSITIONS = {
  0: 'south',
  1: 'west',
  2: 'north',
  3: 'east',
}

function App() {
  const [gameId, setGameId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [hand, setHand] = useState([])
  const [shownCard, setShownCard] = useState(null)
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)
  const [bidding, setBidding] = useState(false)

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

  async function checkBidOrPlay(id) {
    const s = await refreshStatus(id)
    await refreshHand(id)
    if (s.taker !== null) {
      setShownCard(null)
      setBidding(false)
    } else {
      const card = await api(`/games/${id}/showncard`)
      setShownCard(card)
      setBidding(true)
    }
  }

  // ---------- actions ----------
  async function createGame() {
    setLoading(true)
    setError(null)
    try {
      const data = await api('/games/', 'POST', { player_name: 'alex', player_id: 0 })
      const id = data.game_id
      setGameId(id)
      await checkBidOrPlay(id)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function placeBid(takes, suit = null) {
    setError(null)
    try {
      const suitParam = suit ? `&suit=${encodeURIComponent(suit)}` : ''
      const s = await api(`/games/${gameId}/bid?takes=${takes}${suitParam}`, 'POST')
      setStatus(s)
      await refreshHand(gameId)

      if (s.taker !== null) {
        setShownCard(null)
        setBidding(false)
      } else {
        await checkBidOrPlay(gameId)
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
        suit: card.suit,
      })
      setStatus(s)
      await refreshHand(gameId)

      if (!s.game_over) {
        await checkBidOrPlay(gameId)
      }
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
    setBidding(false)
  }

  // ---------- helpers de rendu ----------
  const gameOver = status?.game_over === true
  const bidPhase = bidding && shownCard !== null
  const playPhase = gameId !== null && !bidPhase && !gameOver && status?.taker !== null
  const isSecondRound = status?.bid_round === 2

  // Couleurs disponibles au 2e tour : tout sauf celle de la carte retournée
  const availableSuits = shownCard
    ? ALL_SUITS.filter((s) => s !== shownCard.suit)
    : []

  // current_player → position relative à l'humain (au sud)
  function currentPlayerLabel(idx) {
    if (idx === 0) return 'Vous'
    return `Joueur ${idx} (${POSITIONS[idx]})`
  }

  // Couleur d'une enseigne (rouge / noir)
  function suitClass(suit) {
    return suit === '♥' || suit === '♦' ? 'red' : 'black'
  }

  // Construit un dict { south: card, west: card, ... } à partir d'un dict { 0: card, 1: card, ... }
  function buildPositionedCards(cardsByPlayerIndex) {
    if (!cardsByPlayerIndex) return {}
    const result = {}
    for (const [idx, card] of Object.entries(cardsByPlayerIndex)) {
      result[POSITIONS[idx]] = card
    }
    return result
  }

  // Pli en cours : status.cards_played est une liste, il faut savoir qui a commencé
  // pour mapper position → carte. On utilise starting_player + ordre.
  function buildCurrentTrickPositions() {
    if (!status?.cards_played || status.cards_played.length === 0) return {}
    const result = {}
    const start = status.starting_player
    status.cards_played.forEach((card, i) => {
      const playerIdx = (start + i) % 4
      result[POSITIONS[playerIdx]] = card
    })
    return result
  }

  const currentTrick = buildCurrentTrickPositions()
  const lastTrick = buildPositionedCards(status?.cards_played_last_trick)

  // ---------- rendu ----------
  return (
    <div className="app">
      <h1 className="title">Belote Online</h1>

      {error && <p className="error">{error}</p>}

      {/* --- Ecran d'accueil --- */}
      {gameId === null && (
        <div className="welcome">
          <button className="btn btn-main" onClick={createGame} disabled={loading}>
            {loading ? 'Création...' : 'Nouvelle partie'}
          </button>
        </div>
      )}

      {/* --- Jeu actif --- */}
      {gameId !== null && !gameOver && (
        <div className="game-layout">
          {/* Sidebar : pli précédent */}
          <aside className="sidebar">
            <h3>Pli précédent</h3>
            {Object.keys(lastTrick).length > 0 ? (
              <div className="mini-table">
                <div className="mini-spot mini-north">
                  {lastTrick.north && (
                    <div className={`card mini-card ${suitClass(lastTrick.north.suit)}`}>
                      {lastTrick.north.rank}{lastTrick.north.suit}
                    </div>
                  )}
                </div>
                <div className="mini-spot mini-west">
                  {lastTrick.west && (
                    <div className={`card mini-card ${suitClass(lastTrick.west.suit)}`}>
                      {lastTrick.west.rank}{lastTrick.west.suit}
                    </div>
                  )}
                </div>
                <div className="mini-spot mini-east">
                  {lastTrick.east && (
                    <div className={`card mini-card ${suitClass(lastTrick.east.suit)}`}>
                      {lastTrick.east.rank}{lastTrick.east.suit}
                    </div>
                  )}
                </div>
                <div className="mini-spot mini-south">
                  {lastTrick.south && (
                    <div className={`card mini-card ${suitClass(lastTrick.south.suit)}`}>
                      {lastTrick.south.rank}{lastTrick.south.suit}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <p className="muted">Aucun pli joué</p>
            )}
          </aside>

          {/* Zone principale */}
          <main className="main">
            {/* Scores */}
            {status && (
              <div className="scores">
                <span>Nous : {status.team_ns_points}</span>
                <span>Eux : {status.team_ew_points}</span>
                {status.taker != null && <span>Preneur : {currentPlayerLabel(status.taker)}</span>}
                {status.trump_suit && (
                  <span>Atout : <span className={suitClass(status.trump_suit)}>{status.trump_suit}</span></span>
                )}
              </div>
            )}

            {/* La table */}
            <div className="table">
              <div className="seat seat-north">
                <div className="seat-label">Joueur 2 (Nord)</div>
                {currentTrick.north && (
                  <div className={`card ${suitClass(currentTrick.north.suit)}`}>
                    {currentTrick.north.rank}{currentTrick.north.suit}
                  </div>
                )}
              </div>

              <div className="seat seat-west">
                <div className="seat-label">Joueur 1 (Ouest)</div>
                {currentTrick.west && (
                  <div className={`card ${suitClass(currentTrick.west.suit)}`}>
                    {currentTrick.west.rank}{currentTrick.west.suit}
                  </div>
                )}
              </div>

              <div className="seat seat-east">
                <div className="seat-label">Joueur 3 (Est)</div>
                {currentTrick.east && (
                  <div className={`card ${suitClass(currentTrick.east.suit)}`}>
                    {currentTrick.east.rank}{currentTrick.east.suit}
                  </div>
                )}
              </div>

              {/* Centre : phase enchères ou indicateur */}
              <div className="table-center">
                {bidPhase && (
                  <div className="bid-zone">
                    <p className="info">
                      {isSecondRound ? '2e tour : choisissez une couleur' : 'Carte retournée :'}
                    </p>
                    <div className={`card card-shown ${suitClass(shownCard.suit)}`}>
                      {shownCard.rank}{shownCard.suit}
                    </div>

                    {!isSecondRound ? (
                      <div className="bid-buttons">
                        <button className="btn btn-take" onClick={() => placeBid(true)}>
                          Prendre
                        </button>
                        <button className="btn btn-pass" onClick={() => placeBid(false)}>
                          Passer
                        </button>
                      </div>
                    ) : (
                      <div className="bid-buttons">
                        {availableSuits.map((suit) => (
                          <button
                            key={suit}
                            className="btn btn-suit"
                            onClick={() => placeBid(true, suit)}
                          >
                            <span className={suitClass(suit)}>{suit}</span>
                          </button>
                        ))}
                        <button className="btn btn-pass" onClick={() => placeBid(false)}>
                          Passer
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {playPhase && status && (
                  <div className="turn-info">
                    Tour de : <strong>{currentPlayerLabel(status.current_player)}</strong>
                  </div>
                )}
              </div>

              {/* Sud : zone de l'humain (cartes affichées hors-table) */}
              <div className="seat seat-south">
                {currentTrick.south && (
                  <div className={`card ${suitClass(currentTrick.south.suit)}`}>
                    {currentTrick.south.rank}{currentTrick.south.suit}
                  </div>
                )}
                <div className="seat-label">Vous (Sud)</div>
              </div>
            </div>

            {/* Main du joueur */}
            {hand.length > 0 && (
              <div className="hand">
                {hand.map((card, i) => (
                  <button
                    key={i}
                    className={`card card-hand ${playPhase && status?.current_player === 0 ? 'playable' : ''}`}
                    disabled={!playPhase || status?.current_player !== 0}
                    onClick={() => playCard(card)}
                  >
                    <span className={suitClass(card.suit)}>
                      {card.rank}{card.suit}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </main>
        </div>
      )}

      {/* --- Game over --- */}
      {gameOver && (
        <div className="welcome">
          <h2>Partie terminée !</h2>
          <p>Nous : {status.team_ns_points} — Eux : {status.team_ew_points}</p>
          <p>{status.team_ns_points > status.team_ew_points ? 'Victoire !' : 'Défaite...'}</p>
          <button className="btn btn-main" onClick={resetGame}>
            Rejouer
          </button>
        </div>
      )}
    </div>
  )
}

export default App