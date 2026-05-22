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

## 🧩 Architecture & Data Flow Overview

Below is the complete flow of how BazaarStream generates, processes, enriches, stores, and serves real-time event data.

### **📌 System Architecture Diagram**

![Architecture Diagram]<img width="886" height="886" alt="image" src="https://github.com/user-attachments/assets/ce6f0ccb-c381-422f-a160-a87e738dc59d" />

---

## 🚀 Features

- **Real-time Event Ingestion & Data Simulation**
- **Apache Kafka** message streaming for durable decoupling
- **AWS Lambda** serverless event processing & validation
- **Neon Database** (Serverless Postgres) as the unified transactional & analytical data store
- **ML-powered Recommendation API** for instant user targeting
- **Production-grade Scalability** with built-in fault tolerance and backpressure handling
- **Dashboard-ready Tables** updated seamlessly in real time

---

## 🏗️ Data Flow & System Components

### **1. Data Simulator (E-commerce Client)**
To mimic real-world traffic patterns effortlessly without a front-end client, BazaarStream uses a **Faker-based Python Simulator**:
- **Purpose:** Generates synthetic user events (product views, cart events, purchases) to emulate active client interactions.
- **Implementation:** Serializes localized data into JSON payloads containing device specs, timestamps, event IDs, IP addresses, and behavioral details, broadcasting them directly to Kafka topics.

### **2. Apache Kafka (Ingestion Box)**
A robust, fault-tolerant central nervous system buffering the simulator/client from downstream persistence.
- **Topics:** `product_views`, `cart_events`, `purchases`
- **Key Benefits:** Decouples generation from ingestion and gracefully handles backpressure. If traffic spikes, Kafka reliably buffers messages until Lambda consumers can process them.

### **3. Serverless Event Processing (AWS Lambda)**
AWS Lambda functions dynamically scale to consume payload messages directly from Kafka partitions in batches.
- **Processing Logic:** 
  - **Consume & Parse:** Receives message batches from Kafka, deserializes JSON structures seamlessly.
  - **Transform & Validate:** Validates core objects, checks for malformed schema records, and applies idempotent constraints.
  - **Store:** Writes the processed interactions consistently into exactly corresponding tables.
  
| Kafka Topic       | Lambda Function         | Responsibility |
|------------------|--------------------------|----------------|
| `product_views`     | `ProcessViewLambda`     | Store raw views, update product popularity |
| `cart_events`       | `ProcessCartLambda`     | Store cart activity, update cart summary |
| `purchases`         | `ProcessPurchaseLambda` | Store purchases, update revenue & purchase history |

### **4. Data Storage (Neon Database)**
Neon (Serverless Postgres) serves as the main unified datastore, efficiently handling roles historically assigned to data lakes and NoSQL stores simultaneously.
- **Why Neon?** Auto-scaling serverless Postgres delivers exceptionally low-latency queries while handling high-throughput write volumes perfectly. 
- **Schema Design:** Tailored for both raw historical archives and highly indexable live aggregations without structural compromise.
- **Tables Maintained:**
  - `raw_product_views`, `raw_cart_events`, `raw_purchases`
  - `user_cart_summary`, `live_revenue`, `user_purchase_history`

---

## 🤖 Machine Learning Layer

### **1. Foundational Offline Model**
- Trains periodically using Neon historical tables  
- Generates collaborative-filtering embeddings  

### **2. Lightweight Real-time Model**
- Generates instant adaptive recommendations  
- Uses fresh events queried directly from Neon  
- Powers the recommendation API endpoint
- <img width="935" height="365" alt="image" src="https://github.com/user-attachments/assets/74805a43-4642-4db5-b1c4-d068cdde13af" />
<img width="935" height="365" alt="image" src="https://github.com/user-attachments/assets/b59a48c1-6ffa-4638-932f-67178d49f84b" />
<img width="940" height="440" alt="image" src="https://github.com/user-attachments/assets/5a7aa35e-4de6-4a53-875e-74569358933c" />
<img width="1053" height="936" alt="image" src="https://github.com/user-attachments/assets/b23c881a-c22a-478d-a093-977a31a8bb92" />

---

## 📈 Dashboards & Observability

Any BI tool connected to Neon can visualize:
- Active sessions, cart trends, and conversion funnels
- Top viewed items and real-time revenue  

Tools supported:
- QuickSight, Grafana, Metabase, Superset  

*Observability and alerting routines are enforced using standard telemetry combinations (like AWS CloudWatch for Lambda executions and Kafka lag tracking) to guarantee robust pipeline health.*

---

# 🐳 Development & Local Setup

## ▶️ **Start Kafka (Docker Single Node)**

```bash
docker run -d --name kafka -p 9092:9092 -e KAFKA_NODE_ID=1 -e KAFKA_PROCESS_ROLES=broker,controller -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER -e KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT -e KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@127.0.0.1:9093 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 -e KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1 -e KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1 -e CLUSTER_ID=local-dev-kafka-1234 confluentinc/cp-kafka:latest
```
