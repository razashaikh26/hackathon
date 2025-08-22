/**
 * Vapi AI Voice Integration Service for Frontend
 * Uses PUBLIC KEY ONLY for secure client-side operations
 */

const BASE_URL = 'http://localhost:8000/api/v1';

interface VapiConfig {
  public_key: string;
  assistant_id: string;
  supported_languages: string[];
  features: {
    voice_calls: boolean;
    real_time_conversation: boolean;
    multi_language: boolean;
    financial_context: boolean;
  };
  endpoints: {
    start_call: string;
    voice_chat: string;
    call_status: string;
    webhook: string;
  };
}

interface VoiceMessage {
  message: string;
  language?: string;
  user_id?: string;
}

interface VoiceResponse {
  success: boolean;
  text_response: string;
  voice_url?: string;
  assistant_id?: string;
  user_message?: string;
  transcription?: string;
  audio_response?: string;
  error?: string;
}

interface CallRequest {
  phone_number: string;
  language?: string;
}

interface CallResponse {
  success: boolean;
  call_id?: string;
  assistant_id?: string;
  error?: string;
}

class VapiVoiceService {
  private config: VapiConfig | null = null;
  private publicKey: string;

  constructor() {
    // Get public key from environment (safe for frontend)
    this.publicKey = process.env.REACT_APP_VAPI_PUBLIC_KEY || '584ce1e5-dc84-43b3-9ec1-40099b3c315f';
  }

  private async apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(`${BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * Initialize Vapi service by fetching public configuration from backend
   */
  async initialize(): Promise<boolean> {
    try {
      const response = await this.apiRequest<{ config: VapiConfig }>('/vapi/config');
      this.config = response.config;
      return true;
    } catch (error) {
      console.error('Failed to initialize Vapi service:', error);
      return false;
    }
  }

  /**
   * Send voice message and get intelligent response
   */
  async sendVoiceMessage(message: VoiceMessage): Promise<VoiceResponse> {
    try {
      if (!this.config) {
        await this.initialize();
      }

      const response = await this.apiRequest<VoiceResponse>('/vapi/voice-chat', {
        method: 'POST',
        body: JSON.stringify({
          message: message.message,
          language: message.language || 'english',
          user_id: message.user_id || 'demo_user'
        })
      });

      return response;
    } catch (error) {
      console.error('Voice message error:', error);
      return {
        success: false,
        text_response: 'Sorry, I encountered an error processing your voice message.',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Start a voice call (phone call integration)
   */
  async startVoiceCall(callRequest: CallRequest): Promise<CallResponse> {
    try {
      if (!this.config) {
        await this.initialize();
      }

      const response = await this.apiRequest<CallResponse>('/vapi/start-call', {
        method: 'POST',
        body: JSON.stringify({
          phone_number: callRequest.phone_number,
          language: callRequest.language || 'english'
        })
      });

      return response;
    } catch (error) {
      console.error('Start call error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to start call'
      };
    }
  }

  /**
   * Get call status
   */
  async getCallStatus(callId: string): Promise<any> {
    try {
      return await this.apiRequest(`/vapi/call-status/${callId}`);
    } catch (error) {
      console.error('Get call status error:', error);
      return { error: 'Failed to get call status' };
    }
  }

  /**
   * End voice call
   */
  async endCall(callId: string): Promise<{ success: boolean; error?: string }> {
    try {
      const response = await this.apiRequest<{ success: boolean; message?: string }>(`/vapi/end-call/${callId}`, {
        method: 'POST'
      });
      return { success: response.success };
    } catch (error) {
      console.error('End call error:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Failed to end call' 
      };
    }
  }

  /**
   * Get voice capabilities
   */
  async getCapabilities(): Promise<any> {
    try {
      return await this.apiRequest('/voice/capabilities');
    } catch (error) {
      console.error('Get capabilities error:', error);
      return { error: 'Failed to get capabilities' };
    }
  }

  /**
   * Get supported languages
   */
  getSupportedLanguages(): string[] {
    return this.config?.supported_languages || ['english', 'hindi', 'tamil', 'telugu'];
  }

  /**
   * Check if service is available
   */
  isAvailable(): boolean {
    return this.config !== null;
  }

  /**
   * Get public configuration (safe to expose)
   */
  getPublicConfig(): Partial<VapiConfig> | null {
    if (!this.config) return null;

    return {
      supported_languages: this.config.supported_languages,
      features: this.config.features,
      assistant_id: this.config.assistant_id
    };
  }

  /**
   * Process enhanced voice message with file upload
   */
  async processVoiceFile(
    audioFile: File, 
    language: string = 'en-IN',
    useVapi: boolean = true
  ): Promise<VoiceResponse> {
    try {
      console.log('🎤 VapiVoiceService.processVoiceFile called with:', {
        fileName: audioFile.name,
        fileSize: audioFile.size,
        fileType: audioFile.type,
        language,
        useVapi
      });

      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('language', language);
      formData.append('user_id', 'demo_user');
      formData.append('use_vapi', useVapi ? 'true' : 'false');

      console.log('🎤 Making request to:', `${BASE_URL}/voice/enhanced-message`);

      const response = await fetch(`${BASE_URL}/voice/enhanced-message`, {
        method: 'POST',
        body: formData
      });

      console.log('🎤 Response status:', response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('🎤 Response error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const result = await response.json();
      console.log('🎤 Response data:', result);

      return result;
    } catch (error) {
      console.error('❌ Voice file processing error:', error);
      return {
        success: false,
        text_response: 'Sorry, I could not process your voice message.',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Text-to-speech conversion
   */
  async textToSpeech(text: string, language: string = 'en-IN'): Promise<{ success: boolean; audio_response?: string; error?: string }> {
    try {
      const response = await this.apiRequest<{ success: boolean; audio_response?: string; error?: string }>('/voice/text-to-speech', {
        method: 'POST',
        body: JSON.stringify({
          text: text,
          language: language
        })
      });

      return response;
    } catch (error) {
      console.error('Text-to-speech error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'TTS failed'
      };
    }
  }
}

// Export singleton instance
export const vapiVoiceService = new VapiVoiceService();
export default vapiVoiceService;

// Export types for use in components
export type {
  VapiConfig,
  VoiceMessage,
  VoiceResponse,
  CallRequest,
  CallResponse
};
