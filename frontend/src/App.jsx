import React, { useRef, useState, useEffect } from 'react'

export default function App() {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [streaming, setStreaming] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    async function start() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true })
        videoRef.current.srcObject = stream
        await videoRef.current.play()
        setStreaming(true)
      } catch (err) {
        console.error('Could not start webcam', err)
      }
    }
    start()
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks()
        tracks.forEach(t => t.stop())
      }
    }
  }, [])

  const captureAndSend = async () => {
    const video = videoRef.current
    const canvas = canvasRef.current
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0)
    const blob = await new Promise(res => canvas.toBlob(res, 'image/jpeg'))
    const fd = new FormData()
    fd.append('file', blob, 'capture.jpg')
    const resp = await fetch('http://127.0.0.1:8001/detect', { method: 'POST', body: fd })
    const data = await resp.json()
    setResult(data)
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>MoodFeed — Webcam</h1>
      <div>
        <video ref={videoRef} style={{ maxWidth: '100%' }} />
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>
      <div style={{ marginTop: 8 }}>
        <button onClick={captureAndSend} disabled={!streaming}>Capture & Detect</button>
      </div>
      {result && (
        <pre style={{ marginTop: 12 }}>{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  )
}
