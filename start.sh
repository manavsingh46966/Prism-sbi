#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PRISM — SBI Customer Acquisition Intelligence"
echo "  Predictive Regional Intelligence for Smart Market-entry"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Generate data if not exists
if [ ! -f "backend/data/synthetic/individuals.json" ]; then
  echo "▶ Generating synthetic correlated data..."
  cd backend && python data/generate_data.py && cd ..
  echo "✅ Data generated"
fi

# Start backend
echo "▶ Starting PRISM Backend API (port 8000)..."
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

sleep 2
echo "✅ Backend running at http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"

# Start frontend
echo "▶ Starting PRISM Frontend (port 3000)..."
cd frontend && npm start &
FRONTEND_PID=$!

echo ""
echo "✅ PRISM is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  DEMO FLOW:"
echo "  1. Dashboard    → See live business impact"
echo "  2. Territory    → Click Varanasi pincode zones"  
echo "  3. Leads        → Browse 500 scored individuals"
echo "  4. Engagement   → Trigger live voice/WhatsApp"
echo "  5. Activation   → 90-day journey timelines"
echo "  6. Compliance   → Start live audit stream"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

wait $BACKEND_PID $FRONTEND_PID
