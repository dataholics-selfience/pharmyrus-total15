#!/bin/bash

# Test script for Pharmyrus v4.0 local deployment

BASE_URL="http://localhost:8000"

echo "🧪 Testing Pharmyrus v4.0 API"
echo "================================"
echo ""

# Test 1: Health check
echo "1️⃣  Testing /health"
curl -s "$BASE_URL/health" | python -m json.tool
echo ""
echo ""

# Test 2: WO endpoint
echo "2️⃣  Testing /api/v1/wo/WO2011051540"
curl -s "$BASE_URL/api/v1/wo/WO2011051540" | python -m json.tool | head -50
echo ""
echo ""

# Test 3: Patent endpoint (BR)
echo "3️⃣  Testing /api/v1/patent/BR112012008823B8"
curl -s "$BASE_URL/api/v1/patent/BR112012008823B8" | python -m json.tool | head -50
echo ""
echo ""

# Test 4: Search endpoint (limited)
echo "4️⃣  Testing /api/v1/search (darolutamide, max_wos=2)"
curl -s -X POST "$BASE_URL/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"molecule_name":"darolutamide","max_wos":2,"include_inpi":false}' \
  | python -m json.tool | head -100
echo ""
echo ""

echo "✅ Tests complete!"
