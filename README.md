# Enterprise Operations Copilot

Enterprise Operations Copilot is a grounded document intelligence application built using **Azure AI Search**, **Streamlit**, and a **local LLM via Ollama**. It allows users to search across enterprise knowledge documents such as SOPs, policies, handoff documents, FAQs, and CRM process guides, then generate source-backed answers from the indexed content.

## Project Overview

This project was designed as a portfolio-ready RAG application that demonstrates:

- enterprise document retrieval using Azure AI Search
- grounded answer generation using a local LLM
- a clean frontend built in Streamlit
- source-backed responses based only on indexed documents
- a practical architecture for internal knowledge assistants

The application does not rely on internet search for answers. Instead, it retrieves relevant internal-style documents from Azure AI Search and uses those results as context for answer generation.

## Key Features

- Search across uploaded enterprise documents
- Generate grounded answers using a local Ollama model
- Display source documents used for each answer
- Show supporting search results below the answer
- Clean and simple UI for demo and portfolio use
- Uses only indexed knowledge base content for response generation

## Tech Stack

- **Python**
- **Streamlit**
- **Azure AI Search**
- **Azure Blob Storage**
- **Ollama**
- **Local LLM model:** `gemma3:4b`

## Architecture

The application follows a simple Retrieval-Augmented Generation workflow:

1. The user enters a question in the Streamlit interface
2. Azure AI Search retrieves the most relevant indexed documents
3. The top results are cleaned and combined into context
4. Ollama receives the question plus retrieved context
5. The local model generates a grounded answer
6. The app displays:
   - grounded answer
   - sources used
   - supporting search results

