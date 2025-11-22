# <img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/94fea6c3-221b-4f14-8589-170ac8474ed8" />
 BazaarStream  
### Real-time E-commerce Event Processing, Analytics & Recommendations

![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Kafka](https://img.shields.io/badge/Kafka-Real--time-black)
![AWS](https://img.shields.io/badge/AWS-Serverless-orange)
![Postgres](https://img.shields.io/badge/Neon-Postgres-brightgreen)

BazaarStream is a real-time, serverless data pipeline designed for e-commerce event processing, analytics, and ML-driven recommendations. It processes user interactions with sub-second latency using Kafka, AWS Lambda, Neon Database, and lightweight machine learning models.

---

## 🧩 Architecture Overview

Below is the complete flow of how BazaarStream processes, enriches, stores, and serves real-time event data.

### **📌 System Architecture Diagram**

![Architecture Diagram]<img width="886" height="886" alt="image" src="https://github.com/user-attachments/assets/ce6f0ccb-c381-422f-a160-a87e738dc59d" />

---

## 🚀 Features

- Real-time event ingestion  
- Apache Kafka message streaming  
- AWS Lambda event processing  
- Neon Database (Serverless Postgres) as the unified data store  
- ML-powered recommendation API  
- Production-grade scalability and fault tolerance  
- Dashboard-ready tables updated in real-time  

---

## 🏗️ System Components

### **1. E-commerce Client**
Generates:
- Product views  
- Cart events  
- Purchases  

### **2. Ingestion Service**
- Validates input events  
- Publishes them to Kafka topics  

### **3. Apache Kafka**
Topics used:
- `product_views`
- `cart_events`
- `purchases`

Kafka provides:
- Backpressure handling  
- High throughput  
- Durable event log  

### **4. Event Processing (AWS Lambda)**

| Kafka Topic       | Lambda Function         | Responsibility |
|------------------|--------------------------|----------------|
| `product_views`     | `ProcessViewLambda`     | Store raw views, update product popularity |
| `cart_events`       | `ProcessCartLambda`     | Store cart activity, update cart summary |
| `purchases`         | `ProcessPurchaseLambda` | Store purchases, update revenue & purchase history |

All functions write to **Neon Postgres**.

---

## 🗄️ Data Storage (Neon Database)

Neon is used in place of a data lake.

### **Why Neon?**
- Auto-scaling serverless Postgres  
- Extremely low-latency queries  
- Perfect for both raw and aggregated data  
- ACID-compliant, durable storage  
- Ideal for ML workloads needing SQL access  

### **Tables Stored**
- `raw_product_views`
- `raw_cart_events`
- `raw_purchases`
- `user_cart_summary`
- `live_revenue`
- `user_purchase_history`

---

## 🤖 Machine Learning Layer

### **1. Foundational Offline Model**
- Trains periodically using Neon historical tables  
- Generates collaborative-filtering embeddings  

### **2. Lightweight Real-time Model**
- Generates instant adaptive recommendations  
- Uses fresh events queried directly from Neon  
- Powers the recommendation API endpoint  

---

## 📈 Dashboards

Any BI tool connected to Neon can visualize:
- Active sessions  
- Top viewed items  
- Cart trends  
- Real-time revenue  
- Conversion funnels  

Tools supported:
- QuickSight  
- Grafana  
- Metabase  
- Superset  

---

# 🐳 Development & Local Setup

## ▶️ **Start Kafka (Docker Single Node)**

```bash
docker run -d --name kafka -p 9092:9092 \
-e KAFKA_NODE_ID=1 \
-e KAFKA_PROCESS_ROLES=broker,controller \
-e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER \
-e KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093 \
-e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
-e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT \
-e KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT \
-e KAFKA_CONTROLLER_QUORUM_VOTERS=1@127.0.0.1:9093 \
-e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
-e KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1 \
-e KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1 \
-e CLUSTER_ID=local-dev-kafka-1234 \
confluentinc/cp-kafka:latest
