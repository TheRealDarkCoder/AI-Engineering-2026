# How to execute the scripts

1. Place PDF files in the `papers/` folder.
2. Create a `.env` file with `PROXY_BASE_URL=<api_url>`.
3. Install dependencies: `pip install -r requirements.txt`
4. Run `python indexer.py` to build the FAISS index.
5. Run `python query.py` to start the interactive Q&A assistant. Type your question and press Enter. Type `quit` to exit.

# File names

1. 2402.06664v3.pdf — LLM Agents can Autonomously Hack Websites
2. 2602.05877v1.pdf — Agent2Agent Threats in Safety-Critical LLM Assistants
3. 2410.07283v1.pdf — Prompt Infection: LLM-to-LLM Prompt Injection Within Multi-Agent Systems

# Questions & Answers

1. What methods did the authors use to evaluate GPT-4's ability to autonomously hack websites?

```
[Methods Analyst]
The authors evaluated GPT-4's ability to autonomously hack websites using the following methods:

1. Performing a range of cyberattacks on sandboxed (simulated) websites as test environments to systematically assess the agent's hacking capabilities. They tested against multiple vulnerability types such as SQL injection, CSRF, XSS, SSTI, SSRF, brute force, and others.

2. Measuring quantitative metrics including the average number of function calls (i.e., steps or tool uses) GPT-4 made per successful hack to understand the complexity involved. For example, the average number of function calls for different vulnerabilities ranged from 5 for CSRF to as many as 48 for Webhook XSS, as shown in Table 3 (p.6).

3. Evaluating success rates for each type of vulnerability, demonstrating that easier vulnerabilities like SQL injection and CSRF had 100% success rates, while more complex attacks had lower but still significant success rates (p.6).

4. Conducting ablation studies to identify important factors influencing success, such as the presence or absence of document reading and detailed system instructions, while maintaining necessary components like function calling and context management (p.5).

5. Testing GPT-4 on approximately 50 curated real-world websites, selected based on criteria like being older and potentially unmaintained (which increases vulnerability likelihood). GPT-4 was able to find a real XSS vulnerability on one website during this testing phase (p.7).

In summary, the evaluation combined controlled sandbox experiments with real-world testing, using quantitative metrics of function calls and success rates, as well as ablation studies to analyze components contributing to hacking performance.

This information is based on [2402.06664v3.pdf] pages 5-7.
```

2. What were the main results and success rates of the LLM hacking agents?

```
[Results Extractor]
The main results and success rates of the LLM hacking agents are as follows:

1. GPT-4 agent:
   - Pass @ 5 rate: 73.3%
   - Overall success rate (pass at 1): 42.7%
   - Success rates by vulnerability (success rate over 5 trials each):
     - LFI: 60%
     - CSRF: 100%
     - XSS: 80%
     - SQL Injection: 100%
     - Brute Force: 80%
     - SQL Union: 80%
     - SSTI: 40%
     - Webhook XSS: 20%
     - File upload: 40%
     - SSRF: 20%
     - Hard SQL union: 20%
     - Authorization bypass, Javascript attacks, Hard SQL injection, and XSS + CSRF: 0%
   (Page 7 for vulnerability success rates, Page 5 for overall Pass @ 5 and success rate)

2. GPT-3.5 agent:
   - Pass @ 5 rate: 6.7%
   - Overall success rate: 2.7%
   - Failed to exploit any vulnerability except a single SQL injection.
   - Detected some vulnerabilities but failed to exploit any (OpenChat 3.5 detection rates were generally lower, with 0% exploit success across vulnerabilities)
   (Page 5 and 7)

3. Open-source large models (e.g., LLaMA-70B, Nous Hermes-2 Yi 34B):
   - Essentially 0% success in hacking tests.
   - Fail primarily because of failed tool use and poor planning.
   - No successful exploits.
   (Page 7)

Overall, GPT-4 is by far the most capable agent for autonomous hacking in this study, significantly outperforming GPT-3.5 and open-source LLMs. Detailed prompts and recent LLM agent technology advances are critical for high performance (Page 5).

References:
- 2402.06664v3.pdf, Pages 1, 4, 5, and 7
```

3. What are the key limitations of using LLM agents for autonomous hacking?

```
[Skeptical Reviewer]
The key limitations of using LLM agents for autonomous hacking according to the provided document are:

1. **Failure Causes:** LLM agents can fail due to lack of creativity initially, not pursuing successful strategies to completion, and getting "stuck" on non-working strategies. The choice of the initial prompt is crucial to mitigate these failures, but the best-performing prompts are not fully disclosed for ethical reasons (2402.06664v3.pdf, p.3).

2. **Dependence on Prompting:** Detailed prompts are necessary for good performance. Removing detailed prompts or other contextual documents drastically reduces effectiveness, indicating that the recent LLM agent advancements and prompt design are critical (2402.06664v3.pdf, p.5).

3. **Limited Success on Certain Vulnerabilities:** GPT-4 had zero success with vulnerabilities such as authorization bypass, JavaScript attacks, hard SQL injection, hard SQL union, and combined XSS + CSRF attacks. Success rates for other attacks vary greatly, from as high as 100% on SQL injection and CSRF to as low as 20% or 0% on some other vulnerabilities (2402.06664v3.pdf, p.7).

4. **Open-source LLM Deficits:** Base open-source LLMs largely fail in tool use and planning, which strongly limits their hacking performance. This includes large models like Llama-70B and those tuned on large amounts of GPT-4 data (2402.06664v3.pdf, p.7).

5. **Lack of Human Feedback:** Unlike chatbots or human assistants, these LLM agents do not receive human feedback, which may impair their ability to refine strategies or learn from failure effectively (2402.06664v3.pdf, p.3).

These limitations highlight both technical and operational weaknesses, particularly that effective autonomous hacking by LLM agents currently requires sophisticated prompting and advanced models, and even then, performance varies significantly by vulnerability type. There are vulnerabilities that remain challenging or impossible for LLMs to exploit autonomously.
```

4. What taxonomy or framework is proposed to classify agent-to-agent threats in LLM assistants?

```
[Methods Analyst]
The proposed taxonomy and framework to classify agent-to-agent threats in LLM assistants is called AgentHeLLM (Agent Hazard Exploration for LLM Assistants). It introduces a human-centric asset taxonomy derived from harm-oriented “victim modeling” inspired by the Universal Declaration of Human Rights, and a formal graph-based model that distinguishes poison paths (malicious data propagation) from trigger paths (activation actions). This framework separates asset identification from attack path analysis, adhering to the “separation of concerns” principle standard in safety-critical systems engineering. The framework is demonstrated practically through an open-source tool called AgentHeLLM Attack Path Generator, which automates multi-stage threat discovery using a bi-level search strategy (2602.05877v1.pdf, pp. 1, 13-14).
```

5. What are the main findings regarding the severity of agent-to-agent threats in safety-critical domains?

```
[Results Extractor]
The provided excerpts do not explicitly state detailed findings regarding the severity of agent-to-agent threats in safety-critical domains. However, from the context:

- The paper highlights that existing frameworks like OWASP Agentic AI Threats and MAESTRO co-mingle distinct concepts and are domain-agnostic, thus lacking in addressing the rigorous safety-critical demands where human-centric assets and strict separation of concerns are required (p.2, p.4).
- The proposed AgentHeLLM framework introduces a human-centric asset framework and structured attack path modeling that is applicable to agentic architectures including in-vehicle agents, extending to safety-critical domains (p.12).
- The methodology adapts rigorous safety-critical principles (ISO/SAE 21434 TARA) to the unique risks posed by LLM-based agents, implying that agent-to-agent threats require precise functional separation and traceability to human value harms (p.2, p.4).
- While agent-to-agent threats are addressed via the framework's modeling of actors, datastores, and interaction primitives, no explicit quantitative severity results are detailed in the excerpts (p.12).
- Limitations mention that all edges in the attack path model are treated as equally exploitable, which may oversimplify actual threat severity differences (p.12).

In summary, the main finding is that severe agent-to-agent threats exist in safety-critical domains and require a rigorous, human-centric, and methodologically separated threat modeling approach (AgentHeLLM) that current domain-agnostic models do not provide. This addresses a methodological gap critical for analyzing and mitigating such threats effectively in safety-critical contexts.

Source: 2602.05877v1.pdf, pages 2, 4, 12
```

6. What limitations or gaps does the paper identify in current defenses against agent-to-agent threats?

```
[Skeptical Reviewer]
The paper identifies significant limitations and gaps in current defenses against agent-to-agent (A2A) threats, particularly related to prompt injection attacks in multi-agent systems (MAS). One major gap is that most existing studies focus on inducing errors or noise in agent behaviors but largely overlook the more severe risks posed by prompt injection attacks. These attacks can allow an adversary to fully control compromised systems, enabling activities such as accessing sensitive data, spreading propaganda, disrupting operations, or tricking users into clicking malicious URLs. This gap is attributed to the complexity of MAS architectures, where not all agents are exposed directly to external inputs, making traditional defense paradigms less effective (2410.07283v1.pdf, p.1).

Furthermore, formal attack path models used to analyze these threats assume a fixed architecture and focus primarily on topological path existence rather than the likelihood or difficulty of exploitation. The models treat all interaction edges as equally exploitable, ignoring variations in prompt injection difficulty due to differing guardrails or protections across agents. Additionally, these models require explicitly defined trigger paths and cannot handle scenarios where agents autonomously consume poisoned inputs, such as periodic email polling. There is also a lack of empirical validation with production systems, limiting practical applicability (2602.05877v1.pdf, p.7, 12).

In summary, the key limitations and gaps are:
- Overemphasis on simpler faults rather than full agent compromise via prompt injection.
- Complexity of MAS limiting the exposure and thus the study of injection threats.
- Static, topological defense models that do not capture probabilistic or semantic aspects of attacks.
- Lack of dynamic runtime modeling and empirical validation in real-world systems.

These points illustrate both conceptual and practical gaps in current A2A threat defenses, highlighting avenues for future research and improved security modeling (2410.07283v1.pdf, p.1; 2602.05877v1.pdf, pp.7, 12).
```

7. How does the prompt infection attack propagate between agents in a multi-agent system?

```
[Methods Analyst]
The prompt infection attack propagates between agents in a multi-agent system through a process where a malicious infectious prompt is initially injected into external content like PDFs, emails, or web pages. When an agent interacts with this infected content, it becomes compromised and extracts the infection prompt. The compromised agent then executes specific instructions, updates shared data fields in the prompt, and propagates the infection to downstream agents sequentially. This propagation continues as each compromised agent forwards the infectious prompt to others, ensuring self-replication across the system. The infection leverages components such as Prompt Hijacking (to make agents disregard original instructions), Payload assignment (to delegate tasks according to agent roles), shared Data (for information gathering and transfer), and Self-Replication (to maintain spread across agents) (2410.07283v1.pdf, pp. 3-4).

Moreover, in dynamic multi-agent environments with evolving agent interactions, the infection propagates as agents interact unpredictably, starting from a single infected agent and spreading naturally through the network, achieving widespread system compromise over several interaction turns (2410.07283v1.pdf, p.7).
```

8. What experimental results demonstrate the effectiveness of prompt infection attacks?

```
[Results Extractor]
Experimental results demonstrating the effectiveness of prompt infection attacks include:

1. Self-Replicating infection performs well with three agents, but as the number of agents increases, Non-Replicating infection surpasses Self-Replicating infection by an average of 8.48% in data theft scenarios. This difference is attributed to the complexity of data theft, where efficient cooperation is needed, and Self-Replicating infection introduces additional hurdles due to replication overhead (p.6).

2. The attack success rate for Self-Replicating infection is about 20% lower in local messaging compared to global messaging because prompt infection can fail if even one agent is not compromised in local messaging, while global messaging allows infection to spread via shared message history (p.6).

3. Infection spread timing in larger populations (30, 40, 50 agents) is more efficient relative to the population size. Full infection occurs at about 23.3%, 24.2%, and 21.4% of total turns respectively, indicating faster and more scalable infection spread in larger groups. The spread initially follows exponential growth, slowing down to logistic growth as saturation is approached (p.7).

4. GPT-4o shows fewer failures and more accurate execution of malicious tasks in the “Deformed Infection” category compared to GPT-3.5, which has higher rates of failures, especially in self-replicating infections. Thus, GPT-4o is more resistant yet more dangerous when compromised due to higher precision (p.7).

These results collectively demonstrate both the feasibility and the nuanced dynamics of prompt infection attacks depending on the number of agents, messaging type, and the model version targeted (p.6-7).
```

9. What are the limitations and potential defenses discussed against prompt infection?

```
[Skeptical Reviewer]
The provided context does not explicitly discuss limitations or potential defenses against prompt infection. Instead, it focuses on describing the propagation dynamics of infection prompts in multi-agent environments, the attack scenarios enabled by prompt infection, and the mechanisms by which the infection spreads (e.g., prompt hijacking, payload execution, self-replication) [2410.07283v1.pdf, pp.3, 7]. The document outlines infection spreading patterns and threats such as content manipulation, malware spread, scams, and denial of service but does not offer detailed analysis on limitations of the approach or defenses to mitigate these infections in the given excerpts.

Thus, based on the available context, we cannot provide specifics about the limitations or potential defenses against prompt infection. Further sections of the paper (not provided) might contain such information.
```


# Any additional comments (optional)
