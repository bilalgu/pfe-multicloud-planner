#!/bin/bash

# Script de test pour l'API backend

API_URL="http://localhost:5000"

echo "=== Test de l'API Backend ==="
echo ""

# Test 1: Health check
echo "1. Test health check..."
curl -s "$API_URL/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Génération d'infrastructure simple
echo "2. Test génération infrastructure simple..."
echo "Description: Application web avec base de données MySQL sur AWS"
curl -s -X POST "$API_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux créer une application web avec une base de données MySQL sur AWS"}' \
  | python3 -m json.tool | head -30
echo ""
echo ""

# Test 3: Génération avec plusieurs composants
echo "3. Test génération infrastructure complexe..."
echo "Description: Application avec load balancer, 2 serveurs web et base de données PostgreSQL"
curl -s -X POST "$API_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Je veux une application avec un load balancer, 2 serveurs web et une base de données PostgreSQL sur Azure"}' \
  | python3 -m json.tool | head -30
echo ""
echo ""

# Test 4: Historique
echo "4. Test historique des requêtes..."
curl -s "$API_URL/api/history" | python3 -m json.tool
echo ""

echo "=== Tests terminés ==="
