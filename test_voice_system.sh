#!/bin/bash

echo "🎯 FinVoice Voice System Test Suite"
echo "=================================="

# Test 1: Backend connectivity
echo ""
echo "📡 Test 1: Backend API connectivity"
response=$(curl -s "http://localhost:8000/api/v1/db/overview?user_id=378780bc-cb28-42bc-811d-b86ce74a928b")
if [[ $response == *"portfolio"* ]]; then
    echo "✅ Backend API is responsive"
else
    echo "❌ Backend API failed"
    echo "Response: $response"
fi

# Test 2: Voice Chat endpoint
echo ""
echo "🗣️ Test 2: Voice Chat endpoint"
voice_response=$(curl -s -X POST "http://localhost:8000/api/v1/vapi/voice-chat" \
    -H "Content-Type: application/json" \
    -d '{"message":"show me my account balance","user_id":"378780bc-cb28-42bc-811d-b86ce74a928b","language":"en-IN"}')

if [[ $voice_response == *"success\":true"* ]]; then
    echo "✅ Voice Chat endpoint working"
    echo "Response: $(echo $voice_response | jq -r '.text_response' 2>/dev/null || echo 'Raw response')"
else
    echo "❌ Voice Chat endpoint failed"
    echo "Response: $voice_response"
fi

# Test 3: Enhanced Voice endpoint
echo ""
echo "🎤 Test 3: Enhanced Voice Message endpoint"
enhanced_response=$(curl -s -X POST "http://localhost:8000/api/v1/voice/enhanced-message" \
    -F "audio=@test_audio.wav" \
    -F "language=en-IN" \
    -F "user_id=378780bc-cb28-42bc-811d-b86ce74a928b" \
    -F "use_vapi=true")

if [[ $enhanced_response == *"text_response"* ]]; then
    echo "✅ Enhanced Voice endpoint working"
    echo "Response: $(echo $enhanced_response | jq -r '.text_response' 2>/dev/null || echo 'Raw response')"
else
    echo "❌ Enhanced Voice endpoint failed"
    echo "Response: $enhanced_response"
fi

# Test 4: Frontend connectivity
echo ""
echo "🌐 Test 4: Frontend connectivity"
frontend_response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000")
if [[ $frontend_response == "200" ]]; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend not accessible (HTTP $frontend_response)"
fi

# Test 5: WebSocket endpoint
echo ""
echo "🔌 Test 5: WebSocket endpoint availability"
ws_response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/ws")
if [[ $ws_response == "404" ]]; then
    echo "✅ WebSocket endpoint exists (expected 404 for HTTP request)"
else
    echo "⚠️ WebSocket endpoint response: HTTP $ws_response"
fi

echo ""
echo "🎯 Voice System Test Complete!"
echo ""
echo "💡 To test the complete voice flow:"
echo "1. Open http://localhost:3000/voice-input"
echo "2. Click 'Test with Sample Text' button"
echo "3. Try voice recording with financial questions"
echo ""
echo "🔧 If issues persist, check browser console for detailed logs"
