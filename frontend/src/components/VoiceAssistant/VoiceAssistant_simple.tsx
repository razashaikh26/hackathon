import React, { useState, useRef, useCallback } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import { Mic, MicOff, VolumeUp, Stop } from '@mui/icons-material';
import vapiVoiceService from '../../services/vapiVoiceService';

interface VoiceAssistantProps {
  userId?: string;
  onResponse?: (response: any) => void;
}

const VoiceAssistant: React.FC<VoiceAssistantProps> = ({ userId = 'demo_user', onResponse }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<string>('');
  const [hasPermission, setHasPermission] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Request microphone permission
  const requestPermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setHasPermission(true);
      stream.getTracks().forEach(track => track.stop());
      setError(null);
    } catch (error) {
      setError('Microphone permission required for voice features');
    }
  };

  // Start recording
  const startRecording = async () => {
    if (!hasPermission) {
      await requestPermission();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await processVoiceInput(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setError(null);
    } catch (error) {
      setError('Failed to start recording');
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Process voice input
  const processVoiceInput = async (audioBlob: Blob) => {
    setIsProcessing(true);
    
    try {
      const audioFile = new File([audioBlob], 'voice.webm', { type: 'audio/webm' });
      const response = await vapiVoiceService.processVoiceFile(audioFile, 'en-IN', true);
      
      if (response.success) {
        setLastResponse(response.text_response);
        onResponse?.(response);
      } else {
        setError(response.error || 'Failed to process voice input');
      }
    } catch (error) {
      setError('Failed to process voice input');
    } finally {
      setIsProcessing(false);
    }
  };

  // Test with text input for debugging
  const testWithText = async () => {
    setIsProcessing(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/vapi/voice-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: 'What is my account balance?',
          user_id: userId
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setLastResponse(result.text_response);
        onResponse?.(result);
      } else {
        setError('Failed to get response from server');
      }
    } catch (error) {
      setError('Failed to connect to server');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom align="center">
          Voice Assistant - SQL Financial Queries
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, alignItems: 'center' }}>
          {!hasPermission && (
            <Button
              variant="outlined"
              onClick={requestPermission}
              startIcon={<Mic />}
            >
              Enable Microphone
            </Button>
          )}

          {hasPermission && (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant={isRecording ? "contained" : "outlined"}
                color={isRecording ? "error" : "primary"}
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isProcessing}
                startIcon={isRecording ? <MicOff /> : <Mic />}
                size="large"
              >
                {isRecording ? 'Stop Recording' : 'Start Recording'}
              </Button>

              <Button
                variant="outlined"
                onClick={testWithText}
                disabled={isProcessing}
                startIcon={<VolumeUp />}
              >
                Test Query
              </Button>
            </Box>
          )}

          {isProcessing && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CircularProgress size={20} />
              <Typography variant="body2">Processing...</Typography>
            </Box>
          )}
        </Box>

        {lastResponse && (
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Response:
              </Typography>
              <Typography variant="body1">
                {lastResponse}
              </Typography>
            </CardContent>
          </Card>
        )}

        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Try saying:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            <Chip label="What is my balance?" size="small" />
            <Chip label="Show my expenses" size="small" />
            <Chip label="Portfolio performance" size="small" />
            <Chip label="Financial goals progress" size="small" />
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default VoiceAssistant;
