4 General Equilibrium

Andrea and Bart are agents in a standard Edgeworth Box economy with a total endowment of 10 units of each good. Their utility functions are

$u^{A}(x_{1}^{A},x_{2}^{A})=(x_{1}^{A})^{2}+(x_{2}^{A})^{2}$ and $u^{B}(x_{1}^{B},x_{2}^{B})=x_{1}^{B}+x_{2}^{B}$.

(a) Consider an allocation $x=((x_{1}^{A},x_{2}^{A})$, $(x_{1}^{B},x_{2}^{B}))$ in which $x_{j}^{i}>0$ for $j\in\{1,2\}$ and $i\in\{A,B\}$. Find some allocation that Pareto-dominates $x$.

For questions 1b and 1c, suppose that the initial endowment is $\omega=((7,6),(3,4))$.

(b) Find the core of the economy.

(c) Find the competitive equilibrium. Hint: This should not involve very long algebra if you correctly solve 1b.

PROBLEM SET #8

BSE Microeconomics I
Daniel Sanchez Moscona / Jones Paulson
NOVEMBER 16, 2025

1. Suppose a standard Edgeworth Box economy with total endowments $\omega_{1}=5$ and $\omega_{2}=10$. Suppose preferences are such that:

$$U^{A}(x_{1}^{A},x_{2}^{A})=x_{1}^{A}(x_{2}^{A}+3) \quad \text{and} \quad U^{B}(x_{1}^{B},x_{2}^{B})=x_{1}^{B}(x_{2}^{B}+2)$$

(a) Find the Pareto set in such an economy.

Solution:
Let us start by finding the set of interior Pareto-efficient allocations. In such allocations:

$$MRS_{1,2}^{A}(x_{1}^{A},x_{2}^{A})=MRS_{1,2}^{B}(x_{1}^{B},x_{2}^{B})$$

Therefore, we must solve for:

$$\frac{x_{2}^{A}+3}{x_{1}^{A}}=\frac{x_{2}^{B}+2}{x_{1}^{B}}$$

Since in all non-wasteful allocations $x_{j}^{B}=\omega_{j}-x_{j}^{A}$ for goods $j\in\{1,2\}$, we have that:

$$\frac{x_{2}^{A}+3}{x_{1}^{A}}=\frac{(10-x_{2}^{A})+2}{(5-x_{1}^{A})}=\frac{12-x_{2}^{A}}{5-x_{1}^{A}}$$

Solving for $x_{2}^{A}$ in the equation above yields:

$$x_{2}^{A}=3x_{1}^{A}-3$$

which only makes sense for $x_{1}^{A}\in[1,\frac{13}{3}]$. This is so because for values of $x_{1}^{A}\in[0,1)$, the equation above yields a negative value for $x_{2}^{A}$. Similarly, for values of $x_{1}^{A}\in(\frac{13}{3},5]$ the equation above yields values for $x_{2}^{A}$ that exceed the total endowment. Thus, define the following set of allocations:

$$P_{1}=\{((x_{1}^{A},x_{2}^{A}),(x_{1}^{B},x_{2}^{B})) \mid x_{1}^{A}\in[1,\frac{13}{3}], x_{2}^{A}=3x_{1}^{A}-3, x_{1}^{B}=5-x_{1}^{A}, x_{2}^{B}=10-x_{2}^{A}\}$$

Clearly, all allocations in $P_{1}$ are Pareto-efficient.

It remains to analyze what happens at the border of the Edgeworth Box. We will first see if there are any allocations such that:

$$MRS_{1,2}^{A}(x_{1}^{A},x_{2}^{A}) > MRS_{1,2}^{B}(x_{1}^{B},x_{2}^{B}) \quad \text{and} \quad x_{1}^{B}=0 \text{ or } x_{2}^{A}=0$$

Suppose first that $x_{1}^{B}=0$. Note that $MRS^{B}(0,x_{2}^{B})$ is not defined. However $\lim_{x_{1}^{B}\rightarrow0}MRS^{B}(x_{1}^{B},x_{2}^{B})=\infty$. Hence, it is impossible to find an allocation in which $x_{1}^{B}=0$ and $MRS_{1,2}^{A}(x_{1}^{A},x_{2}^{A})>MRS_{1,2}^{B}(x_{1}^{B},x_{2}^{B})$.

Now suppose that $x_{2}^{A}=0$, which implies that $x_{2}^{B}=10$. Then,

$$MRS_{1,2}^{A}(x_{1}^{A},0)=\frac{3}{x_{1}^{A}}$$

$$MRS_{1,2}^{B}(x_{1}^{B},10)=\frac{12}{x_{1}^{B}}=\frac{12}{5-x_{1}^{A}}$$

Hence, we must solve for:

$$\frac{3}{x_{1}^{A}} > \frac{12}{5-x_{1}^{A}} \iff x_{1}^{A}\in(0,1)$$

Hence, allocations in the following set:

$$P_2 = \{((x_{1}^{A},x_{2}^{A}), (x_{1}^{B},x_{2}^{B})) \mid x_{1}^{A} \in [0,1), x_{2}^{A}=0, x_{1}^{B}=5-x_{1}^{A}, x_{2}^{B}=10\}$$

are also Pareto-efficient.

It remains to check if there are any allocations such that:

$$MRS_{1,2}^{A}(x_{1}^{A},x_{2}^{A}) < MRS_{1,2}^{B}(x_{1}^{B},x_{2}^{B}) \quad \text{and} \quad x_{1}^{A}=0 \text{ or } x_{2}^{B}=0$$

Using the same argument as before, we know that there will not be any such allocations whenever $x_{1}^{A}=0$. Finally, assume $x_{2}^{B}=0$ which implies that $x_{2}^{A}=10$. Then,

$$MRS_{1,2}^{A}(x_{1}^{A},10)=\frac{13}{x_{1}^{A}}$$

$$MRS_{1,2}^{B}(x_{1}^{B},0)=\frac{2}{x_{1}^{B}}=\frac{2}{5-x_{1}^{A}}$$

Hence, we must solve for:

$$\frac{13}{x_{1}^{A}} < \frac{2}{5-x_{1}^{A}} \iff x_{1}^{A}\in(\frac{13}{3},5)$$

Another way of seeing this is the following. Note that when $x_{1}^{B}=0$, B gets zero utility (which, in this case, coincides with his lowest possible level of utility). Hence, the only Pareto-efficient allocation in which B gets zero utility is the one that maximizes A's utility. It is trivial to see that, in this case, this is the allocation in which A gets all the units of both goods in the economy.

Hence, allocations in the following set:

$$P_{3}=\{((x_{1}^{A},x_{2}^{A}),(x_{1}^{B},x_{2}^{B})) \mid x_{1}^{A}\in(\frac{13}{3},5], x_{2}^{A}=10, x_{1}^{B}=10-x_{1}^{A}, x_{2}^{B}=0\}$$

are also Pareto-efficient.

Thus, the Pareto set is given by $P=P_{1}\cup P_{2}\cup P_{3}$.

Figure 1: The Pareto set shows linear segments connecting corners and interior points.

(b) Assume the initial endowment allocation is $\omega=((3,3),(2,7))$. Find the core of the economy. Represent it in an appropriate diagram together with the Pareto set.

Solution:
Graphically, we are looking for the subset of the Pareto set that is individually rational for both agents.

Figure 2: The core of the economy (in orange).

We can see that none of these allocations lie in $P_{2}$ or $P_{3}$ (defined above). In order to verify this, we can see that allocation $((1,0), (4, 10))$ gives A more utility than any allocation in $P_{2}$. However $U^{A}(1,0)=3$, while at the endowment, A's utility is $U^{A}(\omega^{A}) = U^{A}(3,3)=18$. Therefore, no allocation in $P_{2}$ is individually rational from the point of view of A. A symmetric argument allows us to conclude that no allocation in $P_{3}$ is individually rational from the point of view of B.

Thus, we most only focus on allocations in $P_{1}$. Such allocations must satisfy:

$U^{A}(x_{1}^{A},x_{2}^{A})=x_{1}^{A}(x_{2}^{A}+3)\ge18$

$U^{B}(x_{1}^{B},x_{2}^{B})=x_{1}^{B}(x_{2}^{B}+2)\ge18$

Since such allocations are in $P_{1}$, we can rewrite the inequalities above more conveniently. Let us start with (1):

$$x_{1}^{A}((3x_{1}^{A}-3)+3)=3(x_{1}^{A})^{2}\ge18 \implies x_{1}^{A}\ge\sqrt{6}$$

Now, for inequality (2), we will start by rewriting allocations in $P_{1}$ in terms of $x_{1}^{B}$ and $x_{2}^{B}$. Note that for allocations in $P_{1}$ we have that $x_{2}^{A}=3x_{1}^{A}-3$. Hence,

$$10-x_{2}^{B}=3(5-x_{1}^{B})-3 \implies x_{2}^{B}=3x_{1}^{B}-2$$

Therefore, we can now rewrite (2) as:

$$x_{1}^{B}((3x_{1}^{B}-2)+2) \ge 18 \implies 3(x_{1}^{B})^2 \ge 18 \implies x_{1}^{B}\ge\sqrt{6}$$

Hence, to finish off, we rewrite this in terms of $x_{1}^{A}$:

$$(5-x_{1}^{A})\ge\sqrt{6} \implies x_{1}^{A}\le5-\sqrt{6}$$

Putting all of this together, we get that the core is the subset of allocations in $P_{1}$ for which $x_{1}^{A}\in[\sqrt{6},5-\sqrt{6}]$. Formally,

$$C=\{((x_{1}^{A},x_{2}^{A}),(x_{1}^{B},x_{2}^{B})) \mid x_{1}^{A}\in[\sqrt{6},5-\sqrt{6}], x_{2}^{A}=3x_{1}^{A}-3, x_{1}^{B} = 5-x_{1}^{A}, x_{2}^{B} = 10-x_{2}^{A}\}$$

2. Suppose a standard Edgeworth Box economy in which there is a total of 12 units of both goods. Suppose that preferences are such that:

$$U^{A}(x_{1}^{A},x_{2}^{A})=x_{1}^{A}(x_{2}^{A})^{3} \quad \text{and} \quad U^{B}(x_{1}^{B},x_{2}^{B})=x_{1}^{B}+x_{2}^{B}$$

(a) Find the set of interior Pareto-efficient allocations.

Solution:
Interior Pareto-efficient allocations satisfy:

$$MRS_{1,2}^{A}(x_{1}^{A},x_{2}^{A})=MRS_{1,2}^{B}(x_{1}^{B},x_{2}^{B})$$

Therefore, we must solve for:

$$\frac{x_{2}^{A}}{3x_{1}^{A}}=1 \implies x_{2}^{A}=3x_{1}^{A}$$

This only gives interior solutions for $x_{1}^{A}\in(0,4)$. This is so because for values of $x_{1}^{A}\in[4,12]$, the equation above yields values for $x_{2}^{A}$ that exceed the total endowment. Thus, the set of interior Pareto-efficient allocations is the following:

$$P_{1}=\{((x_{1}^{A},x_{2}^{A}), (x_{1}^{B},x_{2}^{B})) \mid x_{1}^{A}\in(0,4), x_{2}^{A}=3x_{1}^{A}, x_{1}^{B}=12-x_{1}^{A}, x_{2}^{B}=12-x_{2}^{A}\}$$

(b) Are there any corner Pareto-efficient allocations (other than the origins of the box)? If so, find them.

Solution:
Clearly, no corner allocation (other than the origins) in which $x_{1}^{A}=0$ or $x_{2}^{A}=0$ can be Pareto-efficient. Now, let us check if there exist allocations in which:

$$MRS_{1,2}^{A}(x_{1}^{A},x_{2}^{A}) > MRS^{B}(x_{1}^{B},x_{2}^{B}) \quad \text{and} \quad x_{1}^{B}=0$$

This requires that:

$$\frac{x_{2}^{A}}{3x_{1}^{A}}>1 \implies x_{2}^{A}>3x_{1}^{A}$$

Knowing that $x_{1}^{B}=0 \implies x_{1}^{A}=12$. Substituting this in the above inequality yields $x_{2}^{A}>36$, which is not possible given the total endowment. Hence, there is no Pareto-efficient allocation (other than the origins) in which $x_{1}^{B}=0$.

Now let us look for Pareto-efficient allocations in which:

$$MRS_{1,2}^{A}(x_{1}^{A},x_{2}^{A}) < MRS^{B}(x_{1}^{B},x_{2}^{B}) \quad \text{and} \quad x_{2}^{B}=0$$

This requires that:

$$\frac{x_{2}^{A}}{3x_{1}^{A}}<1 \implies x_{2}^{A}<3x_{1}^{A}$$

Knowing that $x_{2}^{B}=0 \implies x_{2}^{A}=12$. Substituting in the above inequality yields:

$$12 < 3x_{1}^{A} \implies x_{1}^{A}>4$$

Thus, the allocations in which $x_{1}^{A}\in[4,12]$, $x_{2}^{A}=12$, $x_{1}^{B}=12-x_{1}^{A}$ and $x_{2}^{B}=0$ are Pareto-efficient.

(c) Plot the contract curve in an Edgeworth Box diagram.

Figure 3: The contract curve.

(d) Assume that the initial endowment is $\omega=((6,6), (6,6))$. Find the core of the economy.

Solution:
The core consists of the Pareto-efficient allocations that are individually rational for both agents.

Figure 4: The core of the economy (in orange).

From the diagram, we can infer that the core will only contain interior allocations. Hence, these lie in the line $x_{2}^{A}=3x_{1}^{A}$. Observe also that, at the initial endowment:

$$U^{A}(\omega^{A})=6(6)^3 = 6^4 \quad \text{and} \quad U^{B}(\omega^{B})=6+6=12$$

By individual rationality of A, we know that any allocation in the core must satisfy:

$$U^{A}(x_{1}^{A},x_{2}^{A})=x_{1}^{A}(x_{2}^{A})^{3}\ge6^{4} \implies x_{1}^{A}(3x_{1}^{A})^{3}\ge6^{4} \implies 27(x_{1}^{A})^4 \ge 6^4 \implies x_{1}^{A}\ge \frac{6}{\sqrt[4]{27}} = 2\sqrt[4]{3}\approx2.63$$

By individual rationality of B, we know that any allocation in the core must satisfy:

$$U^{B}(x_{1}^{B},x_{2}^{B})=x_{1}^{B}+x_{2}^{B}\ge12 \implies (12-x_{1}^{A})+(12-x_{2}^{A})\ge12$$

$$\implies 12 \ge x_{1}^{A} + x_{2}^{A} \implies 12 \ge x_{1}^{A} + 3x_{1}^{A} \implies 12 \ge 4x_{1}^{A} \implies x_{1}^{A}\le3$$

Therefore, the core is the following set of allocations:

$$C=\{((x_{1}^{A},x_{2}^{A}),(x_{1}^{B},x_{2}^{B})) \mid x_{1}^{A}\in[2\sqrt[4]{3},3], x_{2}^{A}=3x_{1}^{A}, x_{1}^{B}=12-x_{1}^{A}, x_{2}^{B}=12-x_{2}^{A}\}$$

3. Suppose a standard Edgeworth Box economy in which preferences are given by $U^{A}(x_{1}^{A},x_{2}^{A})=\min\{x_{1}^{A},x_{2}^{A}\}$ and $U^{B}(x_{1}^{B},x_{2}^{B})=\max\{x_{1}^{B},x_{2}^{B}\}$. Assume there is a total of $\omega$ units of each good in the economy.

(a) Draw an Edgeworth Box diagram with some representative indifference curves for each agent.

Solution:
In this case, the indifference curves completely overlap. Thus, the indifference curves in the diagram below are representative of both agents.

Figure 5: Indifference curves (L-shaped for A, Inverse L-shaped for B implied).

(b) Consider the set of non-wasteful allocations that lie on agent A's indifference curve of order $k$ (where $k\in[0,\omega]$). Show analytically (not graphically) that all such allocations provide B with the same level of utility (in other words, they lie on the same indifference curve for agent B).

Solution:
Let $k\in[0,\omega]$. Let us first write the set of allocations that give A a utility of $k$. These are such that:

$$U^{A}(x_{1}^{A},x_{2}^{A})=\min\{x_{1}^{A},x_{2}^{A}\}=k$$

These are the allocations in which one of the following holds:
i. $x_{1}^{A}=k$ and $x_{2}^{A}\ge k$
ii. $x_{1}^{A}\ge k$ and $x_{2}^{A}=k$.

Now, for allocations in which (i) is true, we have that:

$$U^{B}(x_{1}^{B},x_{2}^{B})=\max\{x_{1}^{B},x_{2}^{B}\}=\max\{\omega-k,\omega-x_{2}^{A}\}$$


Since $x_{2}^{A}\ge k \implies -x_{2}^{A} \le -k \implies \omega - x_{2}^{A} \le \omega - k$.
Thus, $\max\{\omega-k, \omega-x_{2}^{A}\} = \omega - k$.

Similarly, for allocations in which (ii) is true, we have that:

$$U^{B}(x_{1}^{B},x_{2}^{B})=\max\{x_{1}^{B},x_{2}^{B}\}=\max\{\omega-x_{1}^{A},\omega-k\}$$


Since $x_{1}^{A}\ge k \implies \omega - x_{1}^{A} \le \omega - k$.
Thus, the max is $\omega - k$.

Hence, all such allocations give B a utility of $\omega-k$, which implies that they lie in the same indifference curve for B.

(c) Using your answer to (3b), find the set of Pareto-efficient allocations in the economy. Provide an economic intuition for your result.

Solution:
In the previous question, we found that whenever A gets a utility of $k\in[0,\omega]$, B gets utility $\omega-k$. That is, the utility of B is strictly decreasing in the utility of A in any allocation. Therefore, all allocations are Pareto-efficient (one cannot increase the utility of one agent without decreasing the utility of the other one).

The intuition for this result is the following. At any allocation, A can get additional utility only by increasing her consumption of the good that she is consuming less of. On the other hand, B gets additional utility by increasing her consumption of the good that she is consuming most of. Given that there is the same total endowment of both the goods, increasing A's utility implies giving her units of the good that B is consuming most of (thereby decreasing B's utility), and vice-versa.

(d) Now suppose the initial endowment allocation is ((4, 1), (2, 5)). Find the core of the economy.

Solution:
Recall that all allocations are Pareto-efficient. Hence, the core of the economy is the subset of allocations that are individually rational for both agents. Since increasing the utility of A implies decreasing the utility of B (and vice-versa), the core consists of the allocations that lie in the indifference curve that passes through the endowment.

$U^A(\omega) = \min\{4,1\} = 1$.
$U^B(\omega) = \max\{2,5\} = 5$.

The core allocations must satisfy $U^A \ge 1$ and $U^B \ge 5$.
Since $U^B = 6 - U^A$ (assuming $\omega=6$ total based on the numbers $4+2=6$ and $1+5=6$), $6-U^A \ge 5 \implies U^A \le 1$.
Thus $U^A=1$ and $U^B=5$.

Hence, the core is:

$$C= \{((x_{1}^{A},x_{2}^{A}), (x_{1}^{B}, x_{2}^{B})) \mid x_{1}^{A}=1, x_{2}^{A} \in [1,6], x_{1}^{B} = 5, x_{2}^{B} = 6-x_{2}^{A}\} \cup \{((x_{1}^{A},x_{2}^{A}), (x_{1}^{B}, x_{2}^{B})) \mid x_{1}^{A} \in [1, 6], x_{2}^{A}=1, x_{1}^{B} = 6-x_{1}^{A}, x_{2}^{B}=5\}$$

Figure 6: The core of the economy (L-shaped line).

4. In an economy, there are 100 euros and one indivisible object, say an art picture.

(a) There are two agents A and B. The value of the picture for A is 10 and for B is 20. Find the set of Pareto efficient allocations in the economy. (Hint: Let an allocation in this context be a tuple $((m_{A},a_{A}), (m_{B},a_{B}))$ where $m_{i}$ is the amount of money held by agent $i$ and $a_{i}$ is a binary variable such that $a_{i}=1$ if $i$ holds the art picture and $a_{i}=0$ otherwise.)

Solution:
Define the following function:
$\mathbb{I}(a_{i})= 1$ if $a_{i}=1$ and $0$ if $a_{i}=0$.

Then, the following utility functions represent the preferences of each agent:
$U_{A}(m_{A},a_{A})=m_{A}+10\mathbb{I}(a_{A})$
$U_{B}(m_{B},a_{B})=m_{B}+20\mathbb{I}(a_{B})$

Feasibility constraints:
$m_{A}+m_{B}=100$
$a_{i}=1 \implies a_{j}=0$.

Let us assume that $m_{A}\le90$. Let us evaluate if any allocation in which A holds the artwork can be Pareto efficient. We are considering any allocation of the form $x^{\prime}=((m_{A}^{\prime},1),(100-m_{A}^{\prime},0))$ where $m_{A}^{\prime}\le90$.

$U_{A}(x^{\prime}) = m_{A}^{\prime}+10$
$U_{B}(x^{\prime}) = 100-m_{A}^{\prime}$

Consider an allocation $x^{*}$ where B holds the item and pays A 10 units (conceptually):
$x^{*}=((m_{A}^{\prime}+10,0),(100-(m_{A}^{\prime}+10),1))$

$U_{A}(x^{*}) = m_{A}^{\prime}+10$
$U_{B}(x^{*}) = 90-m_{A}^{\prime}+20 = 110-m_{A}^{\prime}$

Observe that $U_{B}(x^{*})>U_{B}(x^{\prime})$ and $U_{A}(x^{*})=U_{A}(x^{\prime})$. Hence, $x^{*}$ Pareto-dominates $x^{\prime}$. Thus, it cannot be Pareto efficient that A holds the artwork if B has 10 or more monetary units. However, if B does not have enough money (if $m_{A}^{\prime}>90$) it is efficient that A holds the artwork, since no mutually beneficial exchanges are possible. Hence, the allocations in the following set are Pareto-efficient:

$$S=\{((m_{A},1),(100-m_{A},0)) \mid m_{A}\in(90,100]\}$$

Now, for whatever distribution of money, if B holds the artwork, there are no mutually beneficial exchanges (A values it at 10, B at 20). Hence, any allocation in the following set is also Pareto-efficient:

$$T=\{((m_{A},0),(100-m_{A},1)) \mid m_{A}\in[0,100]\}$$

Set of Pareto-efficient allocations is $S\cup T$.

(b) There are three agents A, B and C. The value of the picture is 10 for A, 20 for B and 50 for C. Find the set of Pareto efficient allocations in this economy.

Solution:
$U_{C}(m_{C},a_{C})=m_{C}+50\mathbb{I}(a_{C})$.

Our conclusion for the previous question still holds. Namely, it cannot be efficient that A holds the artwork if B (or C) has 10 or more monetary units. However, if neither of them have 10 or more monetary units, there are no possible mutually beneficial exchanges. Hence:

$$S=\{((100-m_{B}-m_{C},1),(m_{B},0),(m_{C},0)) \mid 0\le m_{B}<10, 0\le m_{C}<10\}$$

Moreover, extending the same argument implies that it cannot be efficient that B holds the artwork if C has more than 20 monetary units. However, if $m_{C}<20$, no mutually beneficial exchange between B and C exists. Hence:

$$T=\{((100-m_{B}-m_{C},0),(m_{B},1),(m_{C},0)) \mid 0\le m_{C}<20\}$$

Finally, any allocation in which C holds the artwork implies there are no mutually beneficial exchanges (since C has the highest valuation). Hence:

$$V=\{((100-m_{B}-m_{C},0),(m_{B},0),(m_{C},1)) \mid m_{B}\ge0, m_{C}\ge0, m_{B}+m_{C}\le100\}$$

Pareto efficient allocations: $S\cup T\cup V$.

5. Andrea and Bart are two agents in a standard Edgeworth Box economy with two goods. Andrea's and Bart's preferences are such that:

$$U^{A}(x_{1}^{A},x_{2}^{A})=\min\{x_{1}^{A},x_{2}^{A}\} \quad \text{and} \quad U^{B}(x_{1}^{B},x_{2}^{B})=x_{1}^{B}+x_{2}^{B}$$

(a) Suppose that the initial endowment is $\omega=((4,4),(6,6))$. Find the Pareto set and sketch it in an appropriate Edgeworth Box diagram.

Solution:
The Pareto set consists of all the non-wasteful allocations for which $x_{1}^{A}=x_{2}^{A}$. That is:

$$C=\{((x_{1}^{A},x_{2}^{A}),(x_{1}^{B},x_{2}^{B})) \mid x_{1}^{A}\in[0,10], x_{2}^{A}=x_{1}^{A}, x_{1}^{B}=10-x_{1}^{A}, x_{2}^{B}=10-x_{2}^{A}\}$$

Figure: A's indifference curves (red), B's indifference curves (blue) and the Pareto set (green diagonal).

(b) Suppose now that the initial endowment is $\omega=((4,4),(6,1))$. Find the Pareto set and sketch it in an appropriate Edgeworth Box diagram. Provide a brief economic intuition for your result.

Solution:
Total endowment: Good 1 = 10, Good 2 = 5.
The set of Pareto-efficient allocations is given by:

$$P=\{((x_{1}^{A},x_{2}^{A}),(x_{1}^{B},x_{2}^{B})) \mid x_{1}^{A}\in[0,5], x_{2}^{A}=x_{1}^{A}, x_{1}^{B}=10-x_{1}^{A}, x_{2}^{B}=5-x_{2}^{A}\}$$

The main difference with part (a) is that now, the allocation that gives all the goods in the economy to A is no longer Pareto-efficient. This is due to the fact that, once A consumes 5 units of each good (limited by the total amount of good 2), there is no way to further increase her utility. Thus, all Pareto-efficient allocations give B at least 5 units of good 1.

6. Andrea and Bart are two agents in a standard Edgeworth Box economy with initial endowment $\omega=((4,8),(6,2))$. Their utility functions are, respectively:

$$u^{A}(x_{1}^{A},x_{2}^{A})=-(x_{1}^{A}-3)^{2}-(x_{2}^{A}-3)^{2} \quad \text{and} \quad u^{B}(x_{1}^{B},x_{2}^{B})=x_{1}^{B}x_{2}^{B}$$

(a) Draw an Edgeworth Box diagram that includes the initial endowment and at least three representative indifference curves for each agent.

Solution:

Figure 7: Representative indifference curves. A has circular indifference curves centered at (3,3).

(b) Consider the following allocations: $r=((7,7),(3,3))$, $s=((2,1),(8,9))$, $t=((1,1),(9,9))$. Which of these allocations are Pareto-efficient? Justify your answer briefly.

Solution:

Allocation r: Note that no allocation in which $x_{1}^{A}>3$ and $x_{2}^{A}>3$ is Pareto-efficient (all of these points are Pareto-dominated by $((3,3), (7,7))$ because A is satiated at (3,3)). Hence, r is not Pareto-efficient.

Allocation s:


$$MRS^{A}(x_{1}^{A},x_{2}^{A})=\frac{x_{1}^{A}-3}{x_{2}^{A}-3} \quad \text{and} \quad MRS^{B}(x) = \frac{x_{2}^{B}}{x_{1}^{B}}$$


At s, $x^A=(2,1)$. $MRS^A = \frac{2-3}{1-3} = \frac{-1}{-2} = 0.5$.
At s, $x^B=(8,9)$. $MRS^B = \frac{9}{8} = 1.125$.
Since $MRS^A \neq MRS^B$, s is not Pareto-efficient.
(A Pareto-improvement is, for example, allocation $s^{\prime}=((1.5,1.5), (8.5, 8.5))$).

Allocation t:
$x^A=(1,1)$, $x^B=(9,9)$.
$MRS^A = \frac{1-3}{1-3} = 1$.
$MRS^B = \frac{9}{9} = 1$.
Since $MRS^A = MRS^B$ and it belongs in the region where preferences are well-behaved, t is Pareto-efficient.

(c) Find the contract curve in this economy and draw it in an Edgeworth Box diagram.

Solution:
The contract curve is given by the allocations for which $MRS^{A} = MRS^{B}$ and $x_{1}^{A}\le3$, $x_{2}^{A}\le3$.

$$\frac{x_{1}^{A}-3}{x_{2}^{A}-3}=\frac{x_{2}^{B}}{x_{1}^{B}} = \frac{10-x_{2}^{A}}{10-x_{1}^{A}}$$

Using the hint: $\frac{x-a}{y-a}=\frac{b-y}{b-x}$ implies $x=y$.
Here $a=3, b=10$. Thus $x_1^A = x_2^A$.

The contract curve is:

$$P=\{((x_{1}^{A},x_{2}^{A}),(x_{1}^{B},x_{2}^{B})) \mid x_{1}^{A}\in[0,3], x_{2}^{A}=x_{1}^{A}, x_{1}^{B}=10-x_{1}^{A}, x_{2}^{B}=10-x_{2}^{A}\}$$

Figure 8: Contract curve (in orange).