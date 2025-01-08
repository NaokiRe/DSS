$$
V^{new}(S_i) = V^{old}(S_i) + \frac 1 n (r - V^{old}(S_i))
\\
\text{for}\ i=1..n
$$

Inefficient since we treat all steps equally in contributing to the result


$$
V^{new}(S_i) = V^{old}(S_i) + \alpha [R_i - V^{old}(S_i)]
\\
R_n = r \ ;\ R_{n-1}=\gamma V(S_n) \ ;\ R_{n-2}=\gamma V(S_{n-1}) \ ...
$$


$$
V^{new}(\text{winning State}) = V^{old}(\text{winning State}) + \alpha [1 - V^{old}(\text{winning State})]
\\\\
\text{first update}
\\
V^{new}(\text{winning State}) = 0 + \alpha [1 - 0] = \alpha
\\\\
\text{second update}
\\
V^{new}(\text{winning State}) = \alpha + \alpha [1 - \alpha]
$$

$$
V(S_n) = V^{old}(S_n) + \alpha [r - V^{old}(S_n)]
\\
\begin{align}
V(S_{n-1}) &= V^{old}(S_{n-1}) + \alpha [\gamma \{(1-\alpha)V(S_n) + \alpha r \} - V^{old}(S_{n-1})]
\\
&= V^{old}(S_{n-1}) + \alpha [\gamma(1-\alpha)V(S_n) + \alpha \gamma r - V^{old}(S_{n-1})]
\end{align}
$$

![image-20240115203614187](/Users/virineya/Library/Application Support/typora-user-images/image-20240115203614187.png)



