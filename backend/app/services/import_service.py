"""
Service para importação de dados em massa a partir de arquivos Excel.
"""
from typing import Tuple, Optional, List
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime
from ..models import (
    AreaCompetencia, SemestreLetivo, Professor, Disciplina,
    Oferta, Alocacao, TITULACAO_NIVEL_MAP
)
from .area_competencia_service import AreaCompetenciaService
from .semestre_letivo_service import SemestreLetivoService
from .disciplina_service import DisciplinaService
from .professor_service import ProfessorService
from .oferta_service import OfertaService
from .alocacao_service import AlocacaoService


class ImportService:
    """Service para importação de dados em massa."""

    def __init__(self, db: Session):
        self.db = db
        self.area_service = AreaCompetenciaService(db)
        self.semestre_service = SemestreLetivoService(db)
        self.disciplina_service = DisciplinaService(db)
        self.professor_service = ProfessorService(db)
        self.oferta_service = OfertaService(db)
        self.alocacao_service = AlocacaoService(db)

        self.stats = {
            'areas_criadas': 0,
            'areas_existentes': 0,
            'semestres_criados': 0,
            'semestres_existentes': 0,
            'professores_criados': 0,
            'professores_existentes': 0,
            'professores_areas_adicionadas': 0,
            'disciplinas_criadas': 0,
            'disciplinas_existentes': 0,
            'ofertas_criadas': 0,
            'ofertas_existentes': 0,
            'alocacoes_criadas': 0,
            'alocacoes_existentes': 0,
            'erros': []
        }

    def import_from_excel(self, file_path: str) -> Tuple[bool, str]:
        """
        Importa dados de um arquivo Excel.

        Args:
            file_path: Caminho do arquivo Excel

        Returns:
            Tupla (sucesso, mensagem de resultado)
        """
        try:
            # Ler arquivo Excel
            df = pd.read_excel(file_path, engine="openpyxl")

            # Converter datas
            df['DT INCIO DISCIPLINA'] = pd.to_datetime(
                df['DT INCIO DISCIPLINA'], dayfirst=True, errors='coerce'
            )
            df['DT FIM DISCIPLINA'] = pd.to_datetime(
                df['DT FIM DISCIPLINA'], dayfirst=True, errors='coerce'
            )

            # Executar importação
            self._import_areas(df)
            self._import_semestres(df)
            self._import_professores(df)
            self._import_disciplinas(df)
            self._import_ofertas(df)
            self._import_alocacoes(df)

            return True, self._generate_report()

        except FileNotFoundError:
            return False, f"Arquivo não encontrado: {file_path}"
        except Exception as e:
            self.stats['erros'].append(f"Erro geral na importação: {str(e)}")
            return False, self._generate_report()

    def _import_areas(self, df: pd.DataFrame) -> None:
        """Importa áreas de competência."""
        try:
            for nome in df['area_competencia'].dropna().unique():
                area, error = self.area_service.create_if_not_exists(nome=nome)
                if error:
                    self.stats['erros'].append(f"Área {nome}: {error}")
                elif area.id:
                    self.stats['areas_criadas'] += 1
                else:
                    self.stats['areas_existentes'] += 1
        except Exception as e:
            self.stats['erros'].append(f"Erro ao importar áreas: {str(e)}")

    def _import_semestres(self, df: pd.DataFrame) -> None:
        """Importa semestres letivos."""
        try:
            sem_data = df[['PERIODO_LETIVO', 'DT INCIO DISCIPLINA', 'DT FIM DISCIPLINA']]
            sem_data = sem_data.dropna().drop_duplicates()

            for _, row in sem_data.iterrows():
                nome_sem = row['PERIODO_LETIVO']
                ano = int(nome_sem[:4])
                periodo = nome_sem[4:]
                dt_i = row['DT INCIO DISCIPLINA']
                dt_f = row['DT FIM DISCIPLINA']

                existing = self.semestre_service.get_by_nome(nome_sem)
                if existing:
                    self.stats['semestres_existentes'] += 1
                else:
                    semestre, error = self.semestre_service.create_with_validation(
                        nome=nome_sem,
                        ano=ano,
                        periodo=periodo,
                        data_inicio=dt_i,
                        data_fim=dt_f
                    )
                    if error:
                        self.stats['erros'].append(f"Semestre {nome_sem}: {error}")
                    else:
                        self.stats['semestres_criados'] += 1
        except Exception as e:
            self.stats['erros'].append(f"Erro ao importar semestres: {str(e)}")

    def _import_professores(self, df: pd.DataFrame) -> None:
        """Importa professores com áreas de competência."""
        try:
            prof_data = df[['PROFESSOR', 'TITULACAO_PROFESSOR', 'nivel_professor',
                           'area_competencia', 'Horas Máximas Sala/Semestre', 'Modelo de Contratação']]
            prof_data = prof_data.dropna(subset=['PROFESSOR']).drop_duplicates(subset=['PROFESSOR', 'area_competencia'])

            # Agrupar por professor
            prof_groups = prof_data.groupby('PROFESSOR')

            for nome_prof, group in prof_groups:
                existing = self.professor_service.get_by_nome(nome_prof)

                if not existing:
                    # Pegar dados do primeiro registro (são iguais para o mesmo professor)
                    first_row = group.iloc[0]
                    titul = first_row['TITULACAO_PROFESSOR']
                    nivel = int(first_row['nivel_professor'])
                    modelo_contratacao = first_row['Modelo de Contratação']
                    carga_maxima = 256.0 if modelo_contratacao == 'Mensalista ' else 128.0

                    prof, error = self.professor_service.create(
                        nome=nome_prof,
                        titulacao=titul,
                        nivel=nivel,
                        carga_maxima=carga_maxima,
                        modelo_contratacao=modelo_contratacao
                    )

                    if error:
                        self.stats['erros'].append(f"Professor {nome_prof}: {error}")
                        continue

                    self.stats['professores_criados'] += 1
                else:
                    prof = existing
                    self.stats['professores_existentes'] += 1

                # Adicionar áreas
                for _, row in group.iterrows():
                    area_nome = row['area_competencia']
                    area = self.area_service.get_by_nome(area_nome)

                    if area:
                        if area not in prof.areas:
                            prof.areas.append(area)
                            self.stats['professores_areas_adicionadas'] += 1
                            self.db.commit()

        except Exception as e:
            self.stats['erros'].append(f"Erro ao importar professores: {str(e)}")

    def _import_disciplinas(self, df: pd.DataFrame) -> None:
        """Importa disciplinas."""
        try:
            disc_data = df[['DISCIPLINA', 'area_competencia', 'CH_DISCIPLINA', 'nivel_esperado']]
            disc_data = disc_data.dropna(subset=['DISCIPLINA']).drop_duplicates(subset=['DISCIPLINA'])

            for _, row in disc_data.iterrows():
                d_name = row['DISCIPLINA']
                area_nome = row['area_competencia']
                carga = float(row['CH_DISCIPLINA'])
                nivel_esp = int(row['nivel_esperado']) if not pd.isna(row['nivel_esperado']) else 0

                existing = self.disciplina_service.get_by_nome(d_name)
                if existing:
                    self.stats['disciplinas_existentes'] += 1
                else:
                    area = self.area_service.get_by_nome(area_nome)
                    if not area:
                        self.stats['erros'].append(f"Disciplina {d_name}: Área {area_nome} não encontrada")
                        continue

                    disciplina, error = self.disciplina_service.create_with_area(
                        nome=d_name,
                        carga_horaria=carga,
                        nivel_esperado=nivel_esp,
                        area_id=area.id
                    )

                    if error:
                        self.stats['erros'].append(f"Disciplina {d_name}: {error}")
                    else:
                        self.stats['disciplinas_criadas'] += 1

        except Exception as e:
            self.stats['erros'].append(f"Erro ao importar disciplinas: {str(e)}")

    def _import_ofertas(self, df: pd.DataFrame) -> None:
        """Importa ofertas de disciplinas."""
        try:
            oferta_data = df[['PERIODO_LETIVO', 'DISCIPLINA', 'CH_DISCIPLINA']]
            oferta_data = oferta_data.dropna().drop_duplicates()

            for _, row in oferta_data.iterrows():
                sem_nome = row['PERIODO_LETIVO']
                d_nome = row['DISCIPLINA']

                sem = self.semestre_service.get_by_nome(sem_nome)
                disc = self.disciplina_service.get_by_nome(d_nome)

                if not sem or not disc:
                    self.stats['erros'].append(
                        f"Oferta: Semestre {sem_nome} ou Disciplina {d_nome} não encontrado(a)"
                    )
                    continue

                existing = self.oferta_service.exists_duplicate(sem.id, disc.id, "A")

                if existing:
                    self.stats['ofertas_existentes'] += 1
                else:
                    oferta, error = self.oferta_service.create_with_validation(
                        semestre_id=sem.id,
                        disciplina_id=disc.id,
                        turma="A"
                    )

                    if error:
                        self.stats['erros'].append(f"Oferta {d_nome}: {error}")
                    else:
                        self.stats['ofertas_criadas'] += 1

        except Exception as e:
            self.stats['erros'].append(f"Erro ao importar ofertas: {str(e)}")

    def _import_alocacoes(self, df: pd.DataFrame) -> None:
        """Importa alocações de professores a disciplinas."""
        try:
            alloc_data = df[['PERIODO_LETIVO', 'DISCIPLINA', 'PROFESSOR']]
            alloc_data = alloc_data.dropna().drop_duplicates()

            for _, row in alloc_data.iterrows():
                sem_nome = row['PERIODO_LETIVO']
                d_nome = row['DISCIPLINA']
                prof_nome = row['PROFESSOR']

                sem = self.semestre_service.get_by_nome(sem_nome)
                disc = self.disciplina_service.get_by_nome(d_nome)
                prof = self.professor_service.get_by_nome(prof_nome)

                if not sem or not disc or not prof:
                    self.stats['erros'].append(
                        f"Alocação: Semestre {sem_nome}, Disciplina {d_nome} ou Professor {prof_nome} não encontrado(a)"
                    )
                    continue

                oferta = self.oferta_service.exists_duplicate(sem.id, disc.id, "A")
                if not oferta:
                    self.stats['erros'].append(
                        f"Alocação: Oferta para {d_nome} em {sem_nome} não encontrada"
                    )
                    continue

                # Pegar a oferta corretamente
                oferta_obj = self.db.query(Oferta).filter(
                    Oferta.semestre_id == sem.id,
                    Oferta.disciplina_id == disc.id
                ).first()

                existing = self.alocacao_service.get_by_oferta(oferta_obj.id)

                if existing:
                    self.stats['alocacoes_existentes'] += 1
                else:
                    alocacao, error = self.alocacao_service.create_with_validation(
                        oferta_id=oferta_obj.id,
                        professor_id=prof.id
                    )

                    if error:
                        self.stats['erros'].append(f"Alocação {d_nome}-{prof_nome}: {error}")
                    else:
                        self.stats['alocacoes_criadas'] += 1

        except Exception as e:
            self.stats['erros'].append(f"Erro ao importar alocações: {str(e)}")

    def _generate_report(self) -> str:
        """Gera relatório textual da importação."""
        report = [
            "\n" + "="*60,
            "RELATÓRIO DE IMPORTAÇÃO",
            "="*60,
            f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "",
            "📊 RESUMO:",
            f"  Áreas de Competência: {self.stats['areas_criadas']} criadas, {self.stats['areas_existentes']} existentes",
            f"  Semestres Letivos: {self.stats['semestres_criados']} criados, {self.stats['semestres_existentes']} existentes",
            f"  Professores: {self.stats['professores_criados']} criados, {self.stats['professores_existentes']} existentes",
            f"  Áreas de Professores: {self.stats['professores_areas_adicionadas']} adicionadas",
            f"  Disciplinas: {self.stats['disciplinas_criadas']} criadas, {self.stats['disciplinas_existentes']} existentes",
            f"  Ofertas: {self.stats['ofertas_criadas']} criadas, {self.stats['ofertas_existentes']} existentes",
            f"  Alocações: {self.stats['alocacoes_criadas']} criadas, {self.stats['alocacoes_existentes']} existentes",
        ]

        if self.stats['erros']:
            report.append("")
            report.append(f"⚠️  ERROS ({len(self.stats['erros'])}):")
            for erro in self.stats['erros'][:10]:  # Mostrar primeiros 10 erros
                report.append(f"  • {erro}")
            if len(self.stats['erros']) > 10:
                report.append(f"  ... e mais {len(self.stats['erros']) - 10} erros")
        else:
            report.append("")
            report.append("✅ Importação concluída sem erros!")

        report.append("="*60 + "\n")
        return "\n".join(report)

    def import_from_dataframe(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Importa dados a partir de um DataFrame (para uso programático).

        Args:
            df: DataFrame com os dados

        Returns:
            Tupla (sucesso, mensagem de resultado)
        """
        try:
            # Converter datas
            if 'DT INCIO DISCIPLINA' in df.columns:
                df['DT INCIO DISCIPLINA'] = pd.to_datetime(
                    df['DT INCIO DISCIPLINA'], dayfirst=True, errors='coerce'
                )
            if 'DT FIM DISCIPLINA' in df.columns:
                df['DT FIM DISCIPLINA'] = pd.to_datetime(
                    df['DT FIM DISCIPLINA'], dayfirst=True, errors='coerce'
                )

            # Executar importação
            self._import_areas(df)
            self._import_semestres(df)
            self._import_professores(df)
            self._import_disciplinas(df)
            self._import_ofertas(df)
            self._import_alocacoes(df)

            return True, self._generate_report()

        except Exception as e:
            self.stats['erros'].append(f"Erro geral na importação: {str(e)}")
            return False, self._generate_report()

    def get_stats(self) -> dict:
        """Retorna as estatísticas de importação."""
        return self.stats.copy()

