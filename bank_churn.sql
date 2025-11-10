CREATE TABLE IF NOT EXISTS customers (
    RowNumber INT,
    CustomerId BIGINT,
    Surname VARCHAR(50),
    CreditScore INT,
    Geography VARCHAR(50),
    Gender VARCHAR(10),
    Age INT,
    Tenure INT,
    Balance FLOAT,
    NumOfProducts INT,
    HasCrCard INT,
    IsActiveMember INT,
    EstimatedSalary FLOAT,
    Exited INT
);

SELECT 
    COUNT(*) AS total_customers,
    SUM(Exited) AS churned_customers,
    ROUND(100.0 * SUM(Exited)::NUMERIC / COUNT(*), 2) AS churn_rate
FROM customers;

SELECT 
    Geography,
    COUNT(*) AS total_customers,
    SUM(Exited) AS churned_customers,
    ROUND(100.0 * SUM(Exited)::NUMERIC / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY Geography
ORDER BY churn_rate DESC;

SELECT 
    CASE 
        WHEN Age < 30 THEN '<30'
        WHEN Age BETWEEN 30 AND 50 THEN '30-50'
        ELSE '>50'
    END AS age_group,
    COUNT(*) AS total_customers,
    SUM(Exited) AS churned_customers,
    ROUND(100.0 * SUM(Exited)::NUMERIC / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY age_group
ORDER BY churn_rate DESC;

SELECT 
    CASE 
        WHEN Balance = 0 THEN 'No Balance'
        WHEN Balance < 50000 THEN 'Low (<50k)'
        WHEN Balance BETWEEN 50000 AND 100000 THEN 'Medium (50k-100k)'
        ELSE 'High (>100k)'
    END AS balance_group,
    COUNT(*) AS total_customers,
    SUM(Exited) AS churned_customers,
    ROUND(100.0 * SUM(Exited)::NUMERIC / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY balance_group
ORDER BY churn_rate DESC;

SELECT 
    Tenure,
    COUNT(*) AS total_customers,
    SUM(Exited) AS churned_customers,
    ROUND(100.0 * SUM(Exited)::NUMERIC / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY Tenure
ORDER BY Tenure;

SELECT 
    Gender,
    COUNT(*) AS total_customers,
    SUM(Exited) AS churned_customers,
    ROUND(100.0 * SUM(Exited)::NUMERIC / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY Gender
ORDER BY churn_rate DESC;

SELECT 
    NumOfProducts,
    COUNT(*) AS total_customers,
    SUM(Exited) AS churned_customers,
    ROUND(100.0 * SUM(Exited)::NUMERIC / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY NumOfProducts
ORDER BY NumOfProducts;

SELECT 
    CASE 
        WHEN CreditScore < 500 THEN 'Low (<500)'
        WHEN CreditScore BETWEEN 500 AND 700 THEN 'Medium (500-700)'
        ELSE 'High (>700)'
    END AS credit_score_group,
    COUNT(*) AS total_customers,
    SUM(Exited) AS churned_customers,
    ROUND(100.0 * SUM(Exited)::NUMERIC / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY credit_score_group
ORDER BY churn_rate DESC;

SELECT 
    IsActiveMember,
    COUNT(*) AS total_customers,
    SUM(Exited) AS churned_customers,
    ROUND(100.0 * SUM(Exited)::NUMERIC / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY IsActiveMember
ORDER BY churn_rate DESC;

SELECT 
    CASE 
        WHEN EstimatedSalary < 50000 THEN 'Low (<50k)'
        WHEN EstimatedSalary BETWEEN 50000 AND 100000 THEN 'Medium (50k-100k)'
        ELSE 'High (>100k)'
    END AS salary_group,
    COUNT(*) AS total_customers,
    SUM(Exited) AS churned_customers,
    ROUND(100.0 * SUM(Exited)::NUMERIC / COUNT(*), 2) AS churn_rate
FROM customers
GROUP BY salary_group
ORDER BY churn_rate DESC;