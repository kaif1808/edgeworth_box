General Equilibrium

Introduction

Partial Equilibrium: Models of partial equilibrium study the functioning of single markets intentionally abstracting away from circumstances in other markets.

General Equilibrium: Conversely, general equilibrium models study a system of markets, understanding interdependencies.

Context: General equilibrium is a hugely influential and extensive literature. We focus here on the simplest version of this: the exchange economy.

Roadmap:

Description of the setting and main definitions.

Equilibrium definition and properties (existence and the Welfare Theorems).

Applications.

Assumptions and Definitions

Let $\mathcal{I}$ denote a finite set of $I$ individuals.

Let $\mathcal{J}$ denote a finite set of $J$ commodities.

Assumption: Every individual $i \in \mathcal{I}$ possesses a rational, continuous, locally non-satiated preference relation $\succsim^i$.

Assumption: Every individual possesses an initial endowment of every good. Moreover, there is no production, meaning that the total number of units of each good is fixed.

Notation:

$\omega_{j}^{i}$ denotes the number of units of good $j$ that agent $i$ is initially endowed with.

$\omega^{i} \equiv (\omega_{1}^{i}, ..., \omega_{J}^{i})$ refers to the initial consumption bundle that agent $i$ is endowed with.

$\omega_{j} \equiv \sum_{i \in \mathcal{I}} \omega_{j}^{i}$ refers to the total number of units of good $j$.

$\omega \equiv (\omega^{1}, ..., \omega^{I})$ is the initial endowment of the economy.

Allocations

Definition: An allocation is a tuple $x = (x^{1}, ..., x^{I})$ where $x^{i} \equiv (x_{1}^{i}, ..., x_{J}^{i})$ denotes the consumption bundle assigned to individual $i$ according to allocation $x$.

Feasible Allocation: Allocation $x$ is feasible if and only if, for all $j \in \mathcal{J}$:

$$\sum_{i \in \mathcal{I}} x_{j}^{i} \le \sum_{i \in \mathcal{I}} \omega_{j}^{i}$$

Non-wasteful Allocation: Allocation $x$ is non-wasteful if and only if, for all $j \in \mathcal{J}$:

$$\sum_{i \in \mathcal{I}} x_{j}^{i} = \sum_{i \in \mathcal{I}} \omega_{j}^{i}$$

Note: In a $2 \times 2$ exchange economy, the set of non-wasteful allocations can be graphically represented in the Edgeworth Box.

Pareto Efficiency and the Core

Question: What makes an allocation socially desirable?
This is subjective, and we will not be able to fully answer this. However, we want to establish a minimal criterion for social desirability (meaning we want to understand properties that any socially desirable allocation should satisfy, regardless of one's set of values).

Definitions

Pareto Dominance:
An allocation $y$ Pareto-dominates allocation $x$ whenever:

$y$ is feasible.

$u^i(y^i) \ge u^i(x^i)$ for all $i \in \mathcal{I}$, with at least one strict inequality.

Pareto Efficiency:
An allocation $x$ is Pareto-efficient whenever:

$x$ is feasible.

No other allocation Pareto-dominates $x$.

Pareto Set:
We define the Pareto Set as the set of all Pareto-efficient allocations. (Also related to the Contract Curve).

Finding Pareto-Efficient Allocations

Result:
Suppose preferences are strongly monotonic for all $i$. An allocation $\tilde{x}$ is Pareto efficient if and only if it solves the following problem for some values $\bar{U}$:

$$\begin{aligned}
\max \quad & u^i(x^i) \\
\text{s.t.} \quad & u^k(x^k) \ge \bar{U}^k \quad \forall k \in \mathcal{I} \setminus \{i\} \\
& \sum_{i \in \mathcal{I}} x_{j}^{i} \le \sum_{i \in \mathcal{I}} \omega_{j}^{i} \quad \forall j \in \mathcal{J} \\
& x_{j}^{i} \ge 0 \quad \forall i \in \mathcal{I}, j \in \mathcal{J}
\end{aligned}$$

Proofs

$(\Rightarrow)$ Necessity: (If an allocation is PE, then it solves the problem for some $\bar{U}$)
Suppose $x$ is PE but does not solve the problem. Suppose we set $\bar{U}^k = u^k(x^k)$ for $k \ne i$.
Since $x$ does not solve the problem, there must be another feasible allocation $\tilde{x}$ that yields a higher value for the objective function while satisfying constraints.
This implies $u^i(\tilde{x}^i) > u^i(x^i)$ and $u^k(\tilde{x}^k) \ge \bar{U}^k = u^k(x^k)$ for all other agents.
Hence, $\tilde{x}$ Pareto-dominates $x$, which contradicts that $x$ is Pareto efficient.

$(\Leftarrow)$ Sufficiency: (If $x$ solves the problem, then $x$ is PE)
Suppose $x$ solves the problem but is not PE.
Therefore, there exists an allocation $\tilde{x}$ such that $u^i(\tilde{x}^i) \ge u^i(x^i)$ and $u^j(\tilde{x}^j) > u^j(x^j)$ for some $j$.
If $j=i$, $x$ clearly didn't maximize the objective.
If $j \ne i$, consider an allocation $\hat{x}$ adjusted infinitesimally:
$\hat{x}^j = \tilde{x}^j - \epsilon \mathbf{e}$ (where $\mathbf{e} = (1,...1)$ and $\epsilon > 0$)
$\hat{x}^i = \tilde{x}^i + \epsilon \mathbf{e}$
By continuity of $u$, for small enough $\epsilon$, $u^j(\hat{x}^j) \ge u^j(x^j)$ and $u^i(\hat{x}^i) > u^i(x^i)$. This contradicts that $x$ solves the maximization problem.

Solving the Problem (Mathematical Derivation)

We set up the Lagrangian:

$$\mathcal{L} = u^i(x^i) - \sum_{k \in \mathcal{I}\setminus\{i\}} \lambda^k [ \bar{U}^k - u^k(x^k) ] - \sum_{j \in \mathcal{J}} \mu_j \left[ \sum_{i \in \mathcal{I}} (x_j^i - \omega_j^i) \right]$$

(Note: Assuming interior solutions and non-negativity constraints are not binding for simplicity)

First Order Conditions (FOCs):

For agent $i$:


$$\frac{\partial \mathcal{L}}{\partial x_j^i} = \frac{\partial u^i(x^{i*})}{\partial x_j^i} - \mu_j^* = 0$$

For agent $k \ne i$:


$$\frac{\partial \mathcal{L}}{\partial x_j^k} = \lambda^{k*} \frac{\partial u^k(x^{k*})}{\partial x_j^k} - \mu_j^* = 0$$

Constraint binding conditions imply $\lambda^* > 0$ and $\mu^* > 0$.

Interior Solutions:
If we focus on agent $i$ for two commodities $j, k$:

$$\begin{cases}
\frac{\partial u^i}{\partial x_j} = \mu_j \\
\frac{\partial u^i}{\partial x_k} = \mu_k
\end{cases}
\implies \frac{\partial u^i / \partial x_j}{\partial u^i / \partial x_k} = \frac{\mu_j}{\mu_k} \implies MRS_{j,k}^i(x^i) = \frac{\mu_j}{\mu_k}$$

Since this holds for all agents (replacing agent $i$ with agent $k$ and using the multiplier $\lambda^k$ cancels out in the ratio):


$$MRS_{j,k}^i(x^*) = MRS_{j,k}^l(x^*) \quad \forall i, l \in \mathcal{I}$$


(Tangency condition)

Corner Solutions:
Suppose we have a solution where for some agent $i$, $x_j^{i*} = 0$ and $x_k^{i*} > 0$.
From FOCs (incorporating non-negativity multipliers):


$$MRS_{j,k}^i(x^*) \le \frac{\mu_j^*}{\mu_k^*}$$


While for an agent consuming both:


$$MRS_{j,k}^l(x^*) = \frac{\mu_j^*}{\mu_k^*}$$


Hence generally:


$$MRS_{j,k}^i(x^*) \ge MRS_{j,k}^l(x^*)$$

Interpretation

If $MRS_{j,k}^A > MRS_{j,k}^B$:

Agent A is willing to sacrifice more of good $k$ for good $j$ than Agent B requires.

There exists a mutually beneficial exchange (A gives $k$ to B, B gives $j$ to A).

Therefore, the allocation is not Pareto Efficient.

Remarks

Non-Strongly Monotonic Preferences: There can be solutions where utility/feasibility constraints do not bind (e.g., "Leontief" or Min preferences).

Example: $u^A = \min\{x_1^A, x_2^A\}$ and $u^B = \min\{x_1^B, x_2^B\}$.

Efficiency can involve regions ("thick" contract curves) rather than just lines.

Sufficiency: FOCs are necessary. Convexity of preferences assures sufficiency.

Non-differentiable Utility: Problems must be solved via alternative methods (inspection or logical deduction based on indifference curves).

Core of the Economy

Definition: Individual Rationality (IR)
An allocation $x$ is individually rational for agent $i$ if:


$$u^i(x^i) \ge u^i(\omega^i)$$


Meaning: An allocation is IR for $i$ whenever it makes $i$ not worse off than their initial endowment.

Definition: The Core
The Core of the economy is the set of Pareto-efficient allocations that are individually rational for all agents.

It is the segment of the Pareto Set (Contract Curve) bounded by the indifference curves passing through the endowment point $\omega$.

Example: Finding the Core

Setup:

Endowments: $\omega^A = (6, 3)$, $\omega^B = (4, 7)$.

Total Endowment: $\omega_1 = 10, \omega_2 = 10$.

Utility A: $u^A(x_1^A, x_2^A) = x_1^A(x_2^A + 2)$

Utility B: $u^B(x_1^B, x_2^B) = x_1^B x_2^B$

Step 1: Find the Pareto Set
Check for interior solutions: $MRS_{1,2}^A = MRS_{1,2}^B$.


$$MRS^A = \frac{\partial u^A/\partial x_1^A}{\partial u^A/\partial x_2^A} = \frac{x_2^A + 2}{x_1^A}$$

$$MRS^B = \frac{x_2^B}{x_1^B} = \frac{10 - x_2^A}{10 - x_1^A}$$

Equating them:


$$\frac{x_2^A + 2}{x_1^A} = \frac{10 - x_2^A}{10 - x_1^A}$$

$$(x_2^A + 2)(10 - x_1^A) = x_1^A(10 - x_2^A)$$

$$10x_2^A - x_1^A x_2^A + 20 - 2x_1^A = 10x_1^A - x_1^A x_2^A$$

$$10x_2^A + 20 = 12x_1^A$$

$$x_2^A = \frac{6}{5}x_1^A - 2$$


(Equation for the Contract Curve)

Step 2: Check Bounds (Corner Solutions on Contract Curve)

Check where $x_2^A = 0$:
$0 = \frac{6}{5}x_1^A - 2 \implies x_1^A = \frac{10}{6} = \frac{5}{3}$.
For $x_1^A < 5/3$, we hit the boundary $x_2^A=0$.
We verify $MRS^A > MRS^B$ in this region (boundary solution condition).

Check where $x_1^A = 10$:
$x_2^A = 12 - 2 = 10$. This is the top right corner $O^B$.

So the Pareto Set consists of the line $x_2^A = \frac{6}{5}x_1^A - 2$ for $x_1^A \in [\frac{5}{3}, 10]$, plus the segment along the axis where $x_2^A=0$ for $x_1^A \in [0, \frac{5}{3}]$.

Step 3: Find the Core (Apply IR Constraints)
We need allocations on the Pareto Set that satisfy $u \ge u(\omega)$.

Calculate Utility at Endowment:
$u^A(\omega^A) = 6(3+2) = 30$.
$u^B(\omega^B) = 4(7) = 28$.

Check Region 1 (Boundary $x_2^A=0$):
$u^A = x_1^A(0+2) = 2x_1^A$. Max value here is at $x_1^A = 5/3 \implies u^A = 10/3 < 30$.
So no points in the boundary segment are in the Core.

Check Region 2 (Interior Line):
Substitute $x_2^A = \frac{6}{5}x_1^A - 2$ into $u^A \ge 30$:


$$x_1^A \left( \left(\frac{6}{5}x_1^A - 2\right) + 2 \right) \ge 30$$

$$x_1^A \left( \frac{6}{5}x_1^A \right) \ge 30$$

$$\frac{6}{5}(x_1^A)^2 \ge 30 \implies (x_1^A)^2 \ge 25 \implies x_1^A \ge 5$$

Now check $u^B \ge 28$:
Substitute Pareto relationship into B's utility:
$x_1^B = 10 - x_1^A$
$x_2^B = 10 - x_2^A = 10 - (\frac{6}{5}x_1^A - 2) = 12 - \frac{6}{5}x_1^A$.


$$(10 - x_1^A)(12 - \frac{6}{5}x_1^A) \ge 28$$

$$120 - 12x_1^A - 12x_1^A + \frac{6}{5}(x_1^A)^2 \ge 28$$

$$\frac{6}{5}(x_1^A)^2 - 24x_1^A + 92 \ge 0$$


(Solving quadratic for $x_1^A \approx 5.17$)
Actually, looking at the handwritten notes, the calculation approximates the upper bound.
The notes establish the range is roughly $x_1^A \in [5, \approx 5.17]$.

Conclusion:
The Core is the set of allocations where:

$x_2^A = \frac{6}{5}x_1^A - 2$

$x_1^A \in [5, 10 - \sqrt{\frac{70}{3}}]$ (approx 5.17)