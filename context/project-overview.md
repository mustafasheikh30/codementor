# CodeMentor

## Overview

CodeMentor is an AI-powered competitive-programming mentor that helps users improve their problem-solving skills through personalized guidance. It uses the user's Codeforces profile, submission history, and CodeMentor learning activity to understand their strengths, identify struggles, diagnose mistakes, provide progressive hints, recommend relevant problems, and generate progress reports.

## Goals

1. Provide a searchable Codeforces problemset and support code submissions in all programming languages supported by Codeforces.
2. Deliver personalized, AI-powered mentorship that helps users understand problems, overcome difficulties, and improve their problem-solving skills.
3. Track learning activity, identify knowledge gaps, and generate actionable progress reports and recommendations.

## Core User Flow

1. User signs in with their Codeforces account.
2. CodeMentor retrieves the user's available Codeforces profile, rating, and submission history.
3. User browses the problemset or receives personalized problem recommendations.
4. User attempts a problem and submits their code for analysis.
5. CodeMentor analyzes the problem, the user's attempt, and relevant learning history to identify likely mistakes and difficulties.
6. CodeMentor guides the user through progressive hints, explanations, and counterexamples adapted to their needs.
7. CodeMentor records the learning activity, updates the user's learning profile, and recommends appropriate next steps.
8. User reviews progress reports covering strengths, weaknesses, recurring mistakes, and improvement over time.

## Features

### Problem Discovery

- Browse, search, filter, sort, and paginate Codeforces problems.
- View problem details, ratings, tags, and links to the original problem statements.
- Recommend problems based on the user's profile, ability, and learning needs.

### Personalized Mentorship

- Analyze user attempts, failed submissions, and recurring mistakes.
- Identify potential knowledge gaps and areas where the user struggles.
- Provide progressive hints, concept explanations, and counterexamples without immediately revealing complete solutions.
- Adapt guidance to the user's demonstrated skill level and learning history.
- Support code analysis for all programming languages supported by Codeforces.

### Learning History and Reports

- Maintain user accounts through Codeforces authentication.
- Track submissions, diagnoses, hint progression, and practice activity within CodeMentor.
- Use available Codeforces profile and submission data to understand the user's competitive-programming background.
- Generate reports on strengths, weak topics, recurring mistakes, and learning progress.
- Recommend practice problems and learning activities based on the user's performance.

### Code Analysis and Testing

- Diagnose likely logic errors and incorrect assumptions.
- Retrieve similar problems to reinforce relevant concepts.
- Generate counterexamples and test solutions through isolated code execution.
- Support appropriate language-specific compilation and execution where required.

## Scope

### In Scope

- A Codeforces-focused competitive-programming mentorship application.
- Codeforces authentication and profile integration.
- A web interface, API, and PostgreSQL-backed data storage.
- Support for all programming languages supported by Codeforces.
- AI-powered diagnosis, progressive hints, personalized guidance, and progress reports.
- Learning history, similar-problem retrieval, counterexample discovery, and personalized recommendations.
- Secure, isolated code execution with appropriate resource limits.

### Out of Scope

- Replacing Codeforces as a competitive-programming platform.
- Training a large language model from scratch as the initial approach.
- Executing user-submitted code without appropriate isolation and resource limits.

## Success Criteria

1. Users can authenticate through Codeforces and access their CodeMentor profiles and available competitive-programming history.
2. Users can discover Codeforces problems and submit code in supported programming languages for analysis.
3. CodeMentor provides relevant diagnoses and progressive guidance adapted to the user's attempts and learning profile.
4. CodeMentor records learning activity and generates useful reports on recurring mistakes, weak topics, and progress.
5. CodeMentor recommends relevant problems and supports safe testing and counterexample discovery.
