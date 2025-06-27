Claro! Aqui está a tabela em Markdown formatado:

| Critério                              | Tipo  | Como medir                                                                                 | Penalidade / Bônus                                             | Peso (constante)         |
|---------------------------------------|-------|--------------------------------------------------------------------------------------------|----------------------------------------------------------------|---------------------------|
| **1. Cobertura de competência**       | Hard  | Para cada oferta sem `area_id` correspondente no `professor_area_competencia`             | `-P_c` grande penalidade se faltar; `+B_c` bônus se cobrir     | `P_c = 1000`; `B_c = 200` |
| **2. Nível de titulação**             | Soft  | Se `nível_professor ≥ nível_esperado_disciplina`                                          | `+B_n` se nível ≥ esperado                                     | `B_n = 50`                |
| **3. Carga horária máxima**           | Hard  | Para cada professor `p`: `C(p) = ∑ horas alocadas`; `carga_max(p) = 256` ou `128`         | `-P_h × max(0, C(p) − carga_max(p))`                           | `P_h = 5000`              |
| **4. Utilização do corpo docente**    | Hard  | `M = total de professores`, `U = nº com ≥1 alocação`                                      | `-P_u × (M − U)²`                                               | `P_u = 500`               |
| **5. Balanceamento relativo de carga**| Soft  | Para cada `p`: `r(p) = C(p) / carga_max(p)`; calcula `σ_r` (desvio-padrão dos `r`)        | `+B_b × (1 − σ_r)`                                             | `B_b = 100`               |

### Notas:

* **Hard**: são requisitos obrigatórios, soluções devem atender para serem válidas.
* **Soft**: são requisitos desejáveis, soluções podem ser melhores ou piores dependendo do quanto os atendem.

### Destaques:

* Bônus de competência (`200`) > bônus de nível (`50`);
* Penalidade **quadrática** para não uso do corpo docente;
* Penalidade alta para carga horária excedente (`P_h = 5000`).

Pronto para usar em qualquer documentação ou tela de explicação no app!
