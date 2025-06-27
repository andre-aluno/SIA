-- 1. ÁREA DE COMPETÊNCIA
CREATE TABLE area_competencia (
                                  id SERIAL PRIMARY KEY,
                                  nome TEXT UNIQUE NOT NULL
);

-- 2. PROFESSOR
CREATE TABLE professor (
                           id SERIAL PRIMARY KEY,
                           nome TEXT NOT NULL,
                           titulacao TEXT
                               CHECK (titulacao IN ('Ensino Médio','Graduado','Especialista','Mestre','Doutor')),
                           nivel INT
                               CHECK (nivel BETWEEN 0 AND 4),
                           carga_maxima NUMERIC,
                           modelo_contratacao TEXT
                               CHECK (modelo_contratacao IN ('Mensalista ','Horista'))
);

-- 3. VÍNCULO PROFESSOR ↔ ÁREA (N:N)
CREATE TABLE professor_area_competencia (
                                            professor_id INT
                                                REFERENCES professor(id)
                                                    ON DELETE CASCADE,
                                            area_id INT
                                                REFERENCES area_competencia(id)
                                                    ON DELETE CASCADE,
                                            PRIMARY KEY (professor_id, area_id)
);

-- 4. DISCIPLINA (1 disciplina → 1 área)
CREATE TABLE disciplina (
                            id SERIAL PRIMARY KEY,
                            nome TEXT NOT NULL,
                            carga_horaria NUMERIC NOT NULL,
                            nivel_esperado INT
                                CHECK (nivel_esperado BETWEEN 0 AND 4),
                            area_id INT
                                REFERENCES area_competencia(id)
                                    ON DELETE RESTRICT
);

-- 5. SEMESTRE LETIVO
CREATE TABLE semestre_letivo (
                                 id SERIAL PRIMARY KEY,
                                 nome TEXT UNIQUE NOT NULL,   -- ex: '2025-1'
                                 ano INT,
                                 periodo TEXT,
                                 data_inicio DATE,
                                 data_fim DATE
);

-- 6. OFERTA DE DISCIPLINA
CREATE TABLE oferta (
                        id SERIAL PRIMARY KEY,
                        semestre_id INT
                            REFERENCES semestre_letivo(id)
                                ON DELETE CASCADE,
                        disciplina_id INT
                            REFERENCES disciplina(id)
                                ON DELETE CASCADE,
                        turma TEXT
);

-- 7. ALOCAÇÃO DE PROFESSOR (resultado do GA)
CREATE TABLE alocacao (
                          id SERIAL PRIMARY KEY,
                          oferta_id INT
                              REFERENCES oferta(id)
                                  ON DELETE CASCADE,
                          professor_id INT
                              REFERENCES professor(id)
                                  ON DELETE CASCADE
);