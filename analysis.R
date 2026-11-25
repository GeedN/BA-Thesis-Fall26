# analysis.R
# This code implements MANOVA, ANOVA, assumption testing, and descriptive statistics
# Filenames are modifiable so that multiple results csvs can have different output dirs
#
# Coding done with ChatGPT assistance
# Modules used available in standard R installations

# Data handling
library(tidyverse)

# Post-hoc comparisons
library(emmeans)

# Effect sizes
library(effectsize)

# Homogeneity of covariance matrices (Box's M test)
library(biotools)

# Levene's test
library(car)

# power and sensitivity analysis ANOVAS
library(pwr)

#age stats by country
library(dplyr)

df <- read.csv("D:/User/Documents/1_CSAI/Thesis/Data_Exploration/Data/cleaned_filtered_scored_data_10-Nov-26_19-14.csv")

output_dir <- "D:/User/Documents/1_CSAI/Thesis/Data_Exploration/results_3_filtered_data/"
# Create directory if it doesn't already exist
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}
output_dir_section <- "results/"
if (!dir.exists(file.path(output_dir, output_dir_section))) {
  dir.create(file.path(output_dir, output_dir_section), recursive = TRUE)
}

#IVs: condition, country
df$condition <- factor(df$condition)
df$country <- factor(df$country)

outcomes <- c(
  "ses_score",
  "panas_na_diff",
  "panas_pa_diff",
  "tpshri_diff"
)
options(contrasts = c("contr.treatment", "contr.poly"))

model <- manova(
  cbind(
    ses_score,
    panas_na_diff,
    panas_pa_diff,
    tpshri_diff
  ) ~ condition * country,
  data = df
)


summary(  model, test = "Pillai")

residual_cov <- cov(residuals(model))
eigen(cov(residuals(model)))$values
det(cov(residuals(model)))
qr(residuals(model))$rank
qr(as.matrix(df[outcomes]))$rank

# Inspect the model's hypothesis matrices
summary(model, test = "Pillai")

# Check model degrees of freedom
model$rank
model$df.residual

# Check the rank of each hypothesis matrix
sapply(model$SS, function(x) qr(x)$rank)


# ============================================================
# MANOVA RESULTS
# ============================================================

manova_results <- summary(
  model,
  test = "Pillai"
)$stats

results_table <- as.data.frame(manova_results)

results_table$Effect <- rownames(results_table)

rownames(results_table) <- NULL

# Calculate partial eta-squared from approximate F statistics
results_table$Partial_Eta_Squared <- with(
  results_table,
  (`approx F` * Df) /
    ((`approx F` * Df) + `den Df`)
)

# Reorder columns
results_table <- results_table[, c(
  "Effect",
  "Df",
  "Pillai",
  "approx F",
  "num Df",
  "den Df",
  "Pr(>F)",
  "Partial_Eta_Squared"
)]

write.csv(
  results_table,
  file.path(output_dir, output_dir_section, "MANOVA_results.csv"),
  row.names = FALSE
)

# ============================================================
# FOLLOW-UP ANOVAS
# ============================================================
# ============================================================
# FOLLOW-UP ANOVAS WITH PARTIAL ETA-SQUARED
# ============================================================

aov_results <- summary.aov(model)

anova_table <- do.call(rbind, lapply(
  seq_along(aov_results),
  function(i) {

    result <- as.data.frame(aov_results[[i]])

    result$Effect <- rownames(result)
    result$Outcome <- names(aov_results)[i]

    rownames(result) <- NULL

    # Identify residual row (usually the final row)
    residual_row <- which(
      grepl("Residual", result$Effect, ignore.case = TRUE)
    )

    if (length(residual_row) != 1) {
      stop(paste(
        "Could not identify residual row for:",
        names(aov_results)[i],
        "| Available rows:",
        paste(result$Effect, collapse = ", ")
      ))
    }

    residual_ss <- result$`Sum Sq`[residual_row]

    # Calculate partial eta-squared
    result$Partial_Eta_Squared <- NA_real_

    effect_rows <- setdiff(
      seq_len(nrow(result)),
      residual_row
    )

    result$Partial_Eta_Squared[effect_rows] <-
      result$`Sum Sq`[effect_rows] /
      (result$`Sum Sq`[effect_rows] + residual_ss)

    result
  }
))

# Reorder columns
anova_table <- anova_table[, c(
  "Outcome",
  "Effect",
  "Df",
  "Sum Sq",
  "Mean Sq",
  "F value",
  "Pr(>F)",
  "Partial_Eta_Squared"
)]

# Holm correction separately for each effect
anova_table$p_holm <- ave(
  anova_table$`Pr(>F)`,
  anova_table$Effect,
  FUN = function(x) p.adjust(x, method = "holm")
)

# Export
write.csv(
  anova_table,
  file.path(output_dir, output_dir_section, "ANOVA_followup_results.csv"),
  row.names = FALSE
)

# ============================================================
# DESCRIPTIVE STATISTICS
# ============================================================
output_dir_section <- "descriptive_stats/"
if (!dir.exists(file.path(output_dir, output_dir_section))) {
  dir.create(file.path(output_dir, output_dir_section), recursive = TRUE)
}

descriptive_stats <- do.call(rbind, lapply(outcomes, function(outcome) {

  aggregate(
    df[[outcome]],
    by = list(
      condition = df$condition,
      country = df$country
    ),
    FUN = function(x) c(
      mean = mean(x, na.rm = TRUE),
      sd = sd(x, na.rm = TRUE)
    )
  ) |>
    transform(Outcome = outcome)

}))

colnames(descriptive_stats)[1:4] <- c(
  "Condition", "Country", "Mean_SD", "Outcome"
)
write.csv(
  descriptive_stats,
  file.path(output_dir, output_dir_section, "descriptive_statistics.csv"),
  row.names = FALSE
)


# ==========================================
# further demographic analysis: gender, age, education
# ==========================================

# ============================================================
# DEMOGRAPHIC DESCRIPTIVE STATISTICS
# ============================================================

df$gender <- factor(df$gender)
df$education <- factor(df$education)

demographic_variables <- c("gender", "education")

outcomes <- c(
  "ses_score",
  "panas_na_diff",
  "panas_pa_diff",
  "tpshri_diff"
)


# ============================================================
# HELPER FUNCTION: Calculate descriptive statistics
# ============================================================

calculate_stats <- function(x) {

  c(
    N = sum(!is.na(x)),
    Mean = if (all(is.na(x))) NA else mean(x, na.rm = TRUE),
    SD = if (sum(!is.na(x)) < 2) NA else sd(x, na.rm = TRUE)
  )
}


# ============================================================
# 1. CATEGORICAL DEMOGRAPHICS
# ============================================================

demographic_statistics <- do.call(rbind, lapply(
  demographic_variables,
  function(demographic) {

    # Grouping variables
    grouping <- interaction(
      df$condition,
      df$country,
      df[[demographic]],
      drop = TRUE
    )

    # Calculate statistics for each outcome
    result <- aggregate(
      df[outcomes],
      by = list(
        Condition = df$condition,
        Country = df$country,
        Category = df[[demographic]]
      ),
      FUN = calculate_stats
    )

    # Expand each outcome into separate columns
    for (outcome in outcomes) {

      stats <- as.data.frame(result[[outcome]])

      colnames(stats) <- paste0(
        toupper(outcome),
        "_",
        colnames(stats)
      )

      result <- cbind(
        result[, !names(result) %in% outcome, drop = FALSE],
        stats
      )
    }

    result$Demographic <- demographic

    result
  }
))

# Reorder columns
demographic_statistics <- demographic_statistics[, c(
  "Condition",
  "Country",
  "Demographic",
  "Category",
  unlist(lapply(outcomes, function(x) {
    paste0(toupper(x), c("_N", "_Mean", "_SD"))
  }))
)]

# Export
write.csv(
  demographic_statistics,
  file.path(output_dir, output_dir_section, "demographic_statistics.csv"),
  row.names = FALSE
)


# ============================================================
# 2. NUMERICAL DEMOGRAPHIC: AGE
# ============================================================

age_stats <- aggregate(
  df["age"],
  by = list(
    Condition = df$condition,
    Country = df$country
  ),
  FUN = calculate_stats
)

age_stats <- as.data.frame(age_stats$age)

colnames(age_stats) <- paste0(
  "Age_",
  colnames(age_stats)
)

age_groups <- aggregate(
  df[outcomes],
  by = list(
    Condition = df$condition,
    Country = df$country
  ),
  FUN = calculate_stats
)

age_statistics <- age_groups[, 1:2]

# Add age statistics
age_statistics <- cbind(
  age_statistics,
  age_stats
)

# Add outcome statistics
for (outcome in outcomes) {

  stats <- as.data.frame(age_groups[[outcome]])

  colnames(stats) <- paste0(
    toupper(outcome),
    "_",
    colnames(stats)
  )

  age_statistics <- cbind(
    age_statistics,
    stats
  )
}

# Export
write.csv(
  age_statistics,
  file.path(output_dir, output_dir_section, "age_statistics.csv"),
  row.names = FALSE
)


# ============================================================
# OVERALL DEMOGRAPHIC STATISTICS
# ============================================================

demographic_variables <- c("gender", "education")

outcomes <- c(
  "ses_score",
  "panas_na_diff",
  "panas_pa_diff",
  "tpshri_diff"
)

demographic_overall_statistics <- do.call(rbind, lapply(
  demographic_variables,
  function(demographic) {

    # Group only by demographic variable
    result <- aggregate(
      df[outcomes],
      by = list(Category = df[[demographic]]),
      FUN = function(x) c(
        Mean = mean(x, na.rm = TRUE),
        SD = sd(x, na.rm = TRUE)
      )
    )

    # Add one participant count per category
    result$N <- as.numeric(table(
      df[[demographic]]
    )[as.character(result$Category)])

    # Expand outcome statistics into separate columns
    for (outcome in outcomes) {

      stats <- as.data.frame(result[[outcome]])

      colnames(stats) <- paste0(
        toupper(outcome),
        "_",
        colnames(stats)
      )

      result <- cbind(
        result[, !names(result) %in% outcome, drop = FALSE],
        stats
      )
    }

    result$Demographic <- demographic

    result
  }
))

# Reorder columns
demographic_overall_statistics <- demographic_overall_statistics[, c(
  "Demographic",
  "Category",
  "N",
  unlist(lapply(outcomes, function(x) {
    paste0(toupper(x), c("_Mean", "_SD"))
  }))
)]

# Export
write.csv(
  demographic_overall_statistics,
  file.path(output_dir, output_dir_section, "demographic_overall_statistics.csv"),
  row.names = FALSE
)


# ============================================================
# ASSUMPTION TESTING: MANOVA AND ANOVAs
# ============================================================
output_dir_section <- "assumptiontesting/"
if (!dir.exists(file.path(output_dir, output_dir_section))) {
  dir.create(file.path(output_dir, output_dir_section), recursive = TRUE)
}

# Prepare complete-case dataset
analysis_df <- df[
  complete.cases(df[, c("condition", "country", outcomes)]),
  c("condition", "country", outcomes)
]

analysis_df <- droplevels(analysis_df)

analysis_df$cell <- interaction(
  analysis_df$condition,
  analysis_df$country,
  drop = TRUE
)

cat("Participants:", nrow(analysis_df), "\n")
cat("Experimental groups:", nlevels(analysis_df$cell), "\n")


# ============================================================
# 1. LEVENE'S TEST: HOMOGENEITY OF VARIANCES
# ============================================================

levene_results <- do.call(
  rbind,
  lapply(outcomes, function(outcome) {

    model <- lm(
      as.formula(paste(outcome, "~ condition * country")),
      data = analysis_df
    )

    result <- car::leveneTest(
      model,
      center = median
    )

    data.frame(
      Test = "Levene",
      Outcome = outcome,
      Group = NA,
      Statistic = as.numeric(result[1, "F value"]),
      df1 = as.numeric(result[1, "Df"]),
      df2 = as.numeric(result[2, "Df"]),
      p = as.numeric(result[1, "Pr(>F)"]),
      Outliers = NA
    )
  })
)


# ============================================================
# 2. BOX'S M: HOMOGENEITY OF COVARIANCE MATRICES
# ============================================================

box_m <- biotools::boxM(
  as.matrix(analysis_df[outcomes]),
  analysis_df$cell
)

box_m_results <- data.frame(
  Test = "Box's M",
  Outcome = "All outcomes",
  Group = NA,
  Statistic = as.numeric(box_m$statistic),
  df1 = NA,
  df2 = NA,
  p = box_m$p.value,
  Outliers = NA
)


# ============================================================
# 3. MARDIA'S TESTS: MULTIVARIATE NORMALITY
# ============================================================

mardia_test <- function(X) {

  X <- as.matrix(X)
  X <- scale(X, center = TRUE, scale = FALSE)

  n <- nrow(X)
  p <- ncol(X)

  S <- cov(X)

  if (n <= p + 1 || qr(S)$rank < p) {
    stop("Insufficient observations or singular covariance matrix.")
  }

  S_inv <- solve(S)

  # Mahalanobis-type cross-products
  A <- X %*% S_inv %*% t(X)

  # Mardia's skewness
  b1p <- sum(A^3) / n^2

  skew_stat <- n * b1p / 6

  skew_df <- p * (p + 1) * (p + 2) / 6

  skew_p <- pchisq(
    skew_stat,
    df = skew_df,
    lower.tail = FALSE
  )

  # Mardia's kurtosis
  distances <- rowSums((X %*% S_inv) * X)

  b2p <- mean(distances^2)

  kurt_stat <- (b2p - p * (p + 2)) /
    sqrt(8 * p * (p + 2) / n)

  kurt_p <- 2 * pnorm(
    abs(kurt_stat),
    lower.tail = FALSE
  )

  list(
    skew_stat = skew_stat,
    skew_df = skew_df,
    skew_p = skew_p,
    kurt_stat = kurt_stat,
    kurt_p = kurt_p
  )
}

mardia_results <- do.call(
  rbind,
  lapply(levels(analysis_df$cell), function(group) {

    X <- as.matrix(
      analysis_df[
        analysis_df$cell == group,
        outcomes,
        drop = FALSE
      ]
    )

    result <- mardia_test(X)

    rbind(
      data.frame(
        Test = "Mardia skewness",
        Outcome = "All outcomes",
        Group = group,
        Statistic = result$skew_stat,
        df1 = result$skew_df,
        df2 = NA,
        p = result$skew_p,
        Outliers = NA
      ),
      data.frame(
        Test = "Mardia kurtosis",
        Outcome = "All outcomes",
        Group = group,
        Statistic = result$kurt_stat,
        df1 = NA,
        df2 = NA,
        p = result$kurt_p,
        Outliers = NA
      )
    )
  })
)


# ============================================================
# 4. MAHALANOBIS DISTANCE: MULTIVARIATE OUTLIERS
# ============================================================

outlier_results <- do.call(
  rbind,
  lapply(levels(analysis_df$cell), function(group) {

    X <- as.matrix(
      analysis_df[
        analysis_df$cell == group,
        outcomes,
        drop = FALSE
      ]
    )

    distances <- mahalanobis(
      X,
      center = colMeans(X),
      cov = cov(X)
    )

    cutoff <- qchisq(
      0.999,
      df = length(outcomes)
    )

    data.frame(
      Test = "Mahalanobis distance",
      Outcome = "All outcomes",
      Group = group,
      Statistic = max(distances),
      df1 = NA,
      df2 = NA,
      p = NA,
      Outliers = sum(distances > cutoff)
    )
  })
)


# ============================================================
# 5. COMBINE AND EXPORT ALL RESULTS
# ============================================================

assumption_results <- rbind(
  levene_results,
  box_m_results,
  mardia_results,
  outlier_results
)

write.csv(
  assumption_results,
  file.path(output_dir, output_dir_section, "assumption_testing_results.csv"),
  row.names = FALSE
)


# ============================================================
# DIAGNOSTIC PLOTS: NORMALITY AND OUTLIERS
# ============================================================

# Create output folder
plot_dir <- file.path(output_dir, output_dir_section, "Diagnostic_Plots")

dir.create(
  plot_dir,
  recursive = TRUE,
  showWarnings = FALSE
)

for (outcome in outcomes) {

  # Fit factorial ANOVA
  model <- lm(
    as.formula(paste(outcome, "~ condition * country")),
    data = analysis_df
  )

  residuals_model <- residuals(model)
  fitted_values <- fitted(model)

  studentized <- rstudent(model)

  # Save high-resolution PNG
  png(
    filename = file.path(
      plot_dir,
      paste0(outcome, "_diagnostics.png")
    ),
    width = 3000,
    height = 3600,
    res = 300
  )

  par(
    mfrow = c(3, 1),
    mar = c(5, 5, 4, 2),
    cex.main = 1.2,
    cex.lab = 1.1
  )

  # ----------------------------------------------------------
  # 1. Q-Q plot: normality of residuals
  # ----------------------------------------------------------

  qqnorm(
    residuals_model,
    main = paste(outcome, "- Q-Q Plot"),
    pch = 19,
    col = "steelblue"
  )

  qqline(
    residuals_model,
    col = "red",
    lwd = 2
  )

  # ----------------------------------------------------------
  # 2. Residuals vs fitted: homogeneity of variance
  # ----------------------------------------------------------

  plot(
    fitted_values,
    residuals_model,
    main = paste(outcome, "- Residuals vs Fitted"),
    xlab = "Fitted values",
    ylab = "Residuals",
    pch = 19,
    col = "steelblue"
  )

  abline(
    h = 0,
    col = "red",
    lwd = 2
  )

  # ----------------------------------------------------------
  # 3. Studentized residuals: potential outliers
  # ----------------------------------------------------------

  plot(
    fitted_values,
    studentized,
    main = paste(outcome, "- Studentized Residuals"),
    xlab = "Fitted values",
    ylab = "Studentized residuals",
    pch = 19,
    col = "steelblue"
  )

  abline(
    h = c(-3, 3),
    col = "red",
    lty = 2,
    lwd = 2
  )

  # Label potential outliers
  outlier_indices <- which(abs(studentized) > 3)

  if (length(outlier_indices) > 0) {
    text(
      fitted_values[outlier_indices],
      studentized[outlier_indices],
      labels = outlier_indices,
      pos = 3,
      cex = 0.8
    )
  }

  dev.off()
}

cat(
  "Diagnostic plots saved to:",
  plot_dir,
  "\n"
)

# ============================================================
# MULTICOLLINEARITY: CORRELATION MATRIX
# ============================================================

cor_matrix <- cor(
  analysis_df[, outcomes],
  use = "complete.obs"
)

write.csv(
  round(cor_matrix, 3),
  file.path(output_dir, output_dir_section, "MANOVA_correlation_matrix.csv")
)

# ============================================================
# MULTICOLLINEARITY: COVARIANCE MATRIX
# ============================================================


eigenvalues <- eigen(
  residual_cov,
  symmetric = TRUE,
  only.values = TRUE
)$values

singularity_results <- data.frame(
  Rank = qr(residual_cov)$rank,
  Expected_Rank = length(outcomes),
  Minimum_Eigenvalue = min(eigenvalues),
  Maximum_Eigenvalue = max(eigenvalues),
  Condition_Number = max(eigenvalues) / min(eigenvalues)
)


write.csv(
  singularity_results,
  file.path(output_dir, output_dir_section, "MANOVA_singularity.csv"),
  row.names = FALSE
)
# ------------------------------------------------------------
# POSTHOC ANOVA POWER ANALYSIS
# ------------------------------------------------------------
output_dir_section <- "posthoc/"
if (!dir.exists(file.path(output_dir, output_dir_section))) {
  dir.create(file.path(output_dir, output_dir_section), recursive = TRUE)
}

anova_power <- do.call(rbind, lapply(outcomes, function(outcome) {

  model <- lm(
    as.formula(paste(outcome, "~ condition * country")),
    data = analysis_df
  )

  anova_result <- anova(model)

  residual_df <- df.residual(model)
  residual_ss <- sum(residuals(model)^2)

  # Exclude residual row
  effect_rows <- which(
    rownames(anova_result) != "Residuals"
  )

  results <- lapply(effect_rows, function(i) {

    ss_effect <- anova_result$`Sum Sq`[i]

    eta_p2 <- ss_effect / (ss_effect + residual_ss)

    cohens_f2 <- eta_p2 / (1 - eta_p2)

    power <- pwr::pwr.f2.test(
      u = anova_result$Df[i],
      v = residual_df,
      f2 = cohens_f2,
      sig.level = 0.05
    )$power

    data.frame(
      Outcome = outcome,
      Effect = rownames(anova_result)[i],
      Partial_Eta_Squared = eta_p2,
      Cohens_f2 = cohens_f2,
      Observed_Power = power
    )
  })

  do.call(rbind, results)
}))

write.csv(
  anova_power,
  file.path(output_dir, output_dir_section, "ANOVA_observed_power.csv"),
  row.names = FALSE
)


# ============================================================
# POSTHOC SENSITIVITY FOR UNIVARIATE ANOVAs
# ============================================================

# Sample size and degrees of freedom
N <- nrow(analysis_df)
residual_df <- N - 4  # four experimental groups

# Sensitivity analysis for each 1-df ANOVA effect
sensitivity <- do.call(rbind, lapply(
  c(0.05, 0.0125),
  function(alpha) {

    result <- pwr::pwr.f2.test(
      u = 1,
      v = residual_df,
      sig.level = alpha,
      power = 0.80
    )

    # Convert Cohen's f-squared to partial eta-squared
    eta_p2 <- result$f2 / (1 + result$f2)

    data.frame(
      Alpha = alpha,
      Power = 0.80,
      Minimum_Cohens_f2 = result$f2,
      Minimum_Partial_Eta_Squared = eta_p2
    )
  }
))


write.csv(
  sensitivity,
  file.path(output_dir, output_dir_section, "ANOVA_sensitivity_analysis.csv"),
  row.names = FALSE
)


# ============================================================
# POST-HOC MANOVA SENSITIVITY ANALYSIS
# Mathematical calculation using noncentral F distribution
# ============================================================

# Actual MANOVA degrees of freedom
df1 <- 4
df2 <- 116

alpha <- 0.05

# Desired statistical power
target_powers <- c(0.80, 0.90)

# ------------------------------------------------------------
# Calculate power for a given noncentrality parameter
# ------------------------------------------------------------

calculate_power <- function(lambda, df1, df2, alpha) {

  critical_F <- qf(
    1 - alpha,
    df1 = df1,
    df2 = df2
  )

  1 - pf(
    critical_F,
    df1 = df1,
    df2 = df2,
    ncp = lambda
  )
}

# ------------------------------------------------------------
# Find minimum detectable noncentrality parameter
# ------------------------------------------------------------

sensitivity_results <- do.call(
  rbind,
  lapply(target_powers, function(target_power) {

    lambda <- uniroot(
      function(x) {
        calculate_power(x, df1, df2, alpha) -
          target_power
      },
      interval = c(0, 10000)
    )$root

    # Convert to partial eta-squared
    eta_squared <- lambda / (lambda + df2)

    data.frame(
      Analysis = "MANOVA",
      Outcomes = 4,
      N = 123,
      df1 = df1,
      df2 = df2,
      Alpha = alpha,
      Target_Power = target_power,
      Noncentrality_Parameter = lambda,
      Minimum_Detectable_Partial_Eta_Squared =
        eta_squared
    )
  })
)

# ------------------------------------------------------------
# Export results
# ------------------------------------------------------------

write.csv(
  sensitivity_results,
  file.path(output_dir, output_dir_section, "MANOVA_sensitivity_analysis.csv"),
  row.names = FALSE
)

# age stats by country
df %>%
  group_by(country) %>%
  summarise(
    mean_age = mean(age, na.rm = TRUE),
    sd_age = sd(age, na.rm = TRUE)
  )
