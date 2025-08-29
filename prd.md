# Product Requirements Document: CrewAI-based Category Mapping

## 1. Overview

This document outlines the requirements for a new `crewai`-based multi-agent component that will be integrated into the existing `auto-mapping` service. This new component will be responsible for mapping products to categories, replacing the current internal logic of the `auto-mapping` service with a more robust and maintainable approach.

## 2. Problem Statement

The current category mapping logic within the `auto-mapping` service, while functional, is complex and difficult to maintain. It relies on a combination of hard-coded logic, keyword matching, and multiple calls to an LLM, making it hard to debug and improve. The goal is to replace this internal logic with a simpler, more transparent, and more powerful system using `crewai`, while keeping the `auto-mapping` service's interface and overall structure intact.

## 3. Goals

*   To replace the internal category mapping logic of the `auto-mapping` service with a `crewai`-based solution.
*   To improve the accuracy and consistency of product-to-category mapping.
*   To create a more maintainable and extensible mapping component.
*   To provide clear validation and feedback loops for the mapping process.

## 4. User Personas

*   **Data Scientist:** Responsible for developing and maintaining the category mapping models.
*   **Data Engineer:** Responsible for the data pipelines that feed product information into the system.
*   **Product Manager:** Responsible for the overall quality and accuracy of the product categorization.

## 5. Functional Requirements

### 5.1. CrewAI Agents

The system will consist of two `crewai` agents:

*   **Mapper Agent:**
    *   **Responsibility:** To map a given product to the most appropriate category path (up to 7 levels).
    *   **Input:** Product information (product name, description, url, breadcrumbs).
    *   **Process:**
        1.  Analyze the product information, prioritizing `url` and `breadcrumbs` if available, along with the product name, to efficiently map the product to a category and reduce token costs.
        2.  If `breadcrumbs` are not available or the `url` does not contain category path information, the agent will then use the `product description` to better understand the product.
        3.  Use its `PGSearchTool` to search the category hierarchy in the database for relevant categories based on the analyzed product information.
        4.  Use an LLM to determine the most appropriate category path for the product from the search results.
        5.  The agent should be able to reason about the product and the category structure to make an informed decision.
    *   **Output:** A dictionary representing the category path with keys `Level 1` to `Level 7`.

*   **Validation Agent:**
    *   **Responsibility:** To validate the category path proposed by the Mapper Agent.
    *   **Input:** The original product information and the category path proposed by the Mapper Agent.
    *   **Process:**
        1.  Review the product information and the proposed category path.
        2.  Use an LLM to assess the correctness of the mapping.
        3.  If the mapping is deemed incorrect or suboptimal, use its `PGSearchTool` to find a more accurate and valid category path from the database.
        4.  The agent should act as a "second opinion" and either approve the mapping or provide an informed, valid correction.
    *   **Output:** A JSON object containing the status, a confidence score, and a corrected path if applicable.
        *   `"status": "approved"`
        *   `"status": "rejected"`
        *   `"confidence_score": float (0.0 - 1.0)`
        *   `"corrected_path": "..."` (if status is "rejected")

### 5.2. Agent Tooling

*   **PGSearchTool:** Both the Mapper Agent and the Validation Agent will be equipped with the `PGSearchTool`.
    *   For the **Mapper Agent**, this is crucial for finding the most relevant category paths efficiently.
    *   For the **Validation Agent**, this allows it to find valid and accurate alternative paths when suggesting corrections, making the validation process more robust.

### 5.3. Data Flow

1.  The `auto-mapping` service receives a product to be mapped.
2.  The service invokes the `crewai` component, passing the product information to the Mapper Agent.
3.  The Mapper Agent proposes a category path.
4.  The product information and the proposed path are passed to the Validation Agent.
5.  The Validation Agent returns its assessment (including status and confidence score).
6.  The final, validated category path is returned by the `crewai` component to the `auto-mapping` service, which then stores it in the database.

### 5.4. Error Handling and Fallbacks

*   If the `crewai` process fails (e.g., LLM error, tool malfunction, invalid output), the system will:
    1.  Log the detailed error associated with the specific product ID.
    2.  Flag the product in the database with a status of `mapping_failed`.
    3.  This will prevent process interruption and allow for easier debugging and manual intervention.

### 5.5. Input Data Structure

The input product data to the `crewai` component will be in the following format:

```json
{
  "product_id": 123,
  "title": "...",
  "description": "...",
  "url": "...",
  "breadcrumbs": [
    "Grocery & Household",
    "Fresh Food",
    "Fruit",
    "Apples & Pears",
    "Apples"
  ]
}
```

### 5.6. Output Data Structure

The final output of the `crewai` component will be in the following format, which will then be returned by the `auto-mapping` service:

```json
{
    "product_id": 123,
    "level_1": "Grocery & Household",
    "level_2": "Fresh Food",
    "level_3": "Fruit",
    "level_4": "Apples & Pears",
    "level_5": "Apples",
    "level_6": null,
    "level_7": null
}
```

## 6. Non-Functional Requirements

*   **Performance:** The system should be able to process a high volume of products in a timely manner.
*   **Scalability:** The system should be able to scale to handle a growing number of products and categories.
*   **Reliability:** The system should be reliable and produce consistent results.
*   **Maintainability:** The code should be well-documented and easy to maintain.

## 7. Implementation Notes

*   The `on-demand-scrapping` directory should be used as a reference for the implementation of the `crewai` workflow. It contains examples of how to set up and run `crewai` agents and tasks.

## 8. Future Enhancements

### 8.1. Continuous Improvement Feedback Loop
*   A mechanism will be implemented to store all mapping results, including rejections and manual corrections, in a dedicated logging table.
*   This data will be used periodically to evaluate agent performance and to fine-tune the prompts and logic for the Mapper and Validation agents, creating a continuous learning cycle.

## 9. Out of Scope

*   This project will not involve any changes to the `auto-mapping` service's public API.
*   This project will not involve any changes to the product scraping or data ingestion pipelines.
*   This project will not involve any changes to the database schema beyond potentially adding a logging table for the feedback loop.
