# llm-provider-integration Specification

## Purpose

Allows the application to use a configured LLM provider and model through a stable integration boundary, so provider choices can change without changing the financial-query workflow.

## Requirements

### Requirement: Use the configured model provider

The application SHALL send each model request to the provider and model selected by its runtime configuration.

#### Scenario: Configured provider and model are selected
- **WHEN** the application processes a request with valid provider and model configuration
- **THEN** it sends the model request to that configured provider and model
