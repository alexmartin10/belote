import { useState } from 'react'

function App() {
  const [gameId, setGameId] = useState(null)
  const [loading, setLoading] = useState(false)

  async function createGame() {
    setLoading(true)
    try {
    const response = await fetch('http://127.0.0.1:8000/games/', {
      method:'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_name: 'alex' , player_id: 0})
    })
    const data = await response.json()    
    const game_id = data['game_id']
    setGameId(game_id)
    } catch (error) {
    console.error(error)
    } finally {
    setLoading(false)  // s'exécute toujours, même en cas d'erreur
    }
  }

  return (
  <>
    <div>
      {loading == true && <p>Création</p>}
      {gameId !== null && <p>Partie créée : {gameId}</p>}
    </div>
    <button
      type="button"
      className="creator"
      onClick={() => createGame()}
    >
      Create game
    </button>
  </>
  )
}

export default App