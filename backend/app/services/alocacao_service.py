"""
Service para gerenciar Alocações de Professores a Disciplinas.
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from ..models import Alocacao, Oferta, Professor, SemestreLetivo, Disciplina
from .base_service import BaseService


class AlocacaoService(BaseService[Alocacao]):
    """Service para operações CRUD de Alocações de Professores."""

    def __init__(self, db: Session):
        super().__init__(Alocacao, db)

    def list_all_ordered(self) -> List[Alocacao]:
        """Lista todas as alocações ordenadas por semestre e disciplina."""
        try:
            return self.db.query(Alocacao).join(
                Alocacao.oferta
            ).join(
                Oferta.semestre
            ).join(
                Oferta.disciplina
            ).order_by(
                SemestreLetivo.nome,
                Disciplina.nome,
                Alocacao.id
            ).all()
        except Exception as e:
            print(f"Erro ao listar alocações: {str(e)}")
            return []

    def get_by_oferta(self, oferta_id: int) -> Optional[Alocacao]:
        """Busca a alocação de uma oferta (uma oferta tem no máximo uma alocação)."""
        try:
            return self.db.query(Alocacao).filter(
                Alocacao.oferta_id == oferta_id
            ).first()
        except Exception as e:
            print(f"Erro ao buscar alocação por oferta: {str(e)}")
            return None

    def get_by_professor(self, professor_id: int) -> List[Alocacao]:
        """Busca todas as alocações de um professor."""
        try:
            return self.db.query(Alocacao).filter(
                Alocacao.professor_id == professor_id
            ).join(
                Alocacao.oferta
            ).join(
                Oferta.disciplina
            ).order_by(
                Disciplina.nome
            ).all()
        except Exception as e:
            print(f"Erro ao listar alocações por professor: {str(e)}")
            return []

    def get_by_semestre(self, semestre_id: int) -> List[Alocacao]:
        """Busca todas as alocações de um semestre."""
        try:
            return self.db.query(Alocacao).join(
                Alocacao.oferta
            ).filter(
                Oferta.semestre_id == semestre_id
            ).join(
                Oferta.disciplina
            ).order_by(
                Disciplina.nome,
                Alocacao.id
            ).all()
        except Exception as e:
            print(f"Erro ao listar alocações por semestre: {str(e)}")
            return []

    def get_by_semestre_nome(self, semestre_nome: str) -> List[Alocacao]:
        """Busca alocações por nome do semestre."""
        try:
            return self.db.query(Alocacao).join(
                Alocacao.oferta
            ).join(
                Oferta.semestre
            ).filter(
                SemestreLetivo.nome == semestre_nome
            ).join(
                Oferta.disciplina
            ).order_by(
                Disciplina.nome,
                Alocacao.id
            ).all()
        except Exception as e:
            print(f"Erro ao listar alocações por semestre: {str(e)}")
            return []

    def exists_for_oferta(self, oferta_id: int) -> bool:
        """Verifica se uma oferta já possui alocação."""
        return self.get_by_oferta(oferta_id) is not None

    def create_with_validation(self, oferta_id: int, professor_id: int) -> tuple[Optional[Alocacao], Optional[str]]:
        """
        Cria uma alocação com validações completas.

        Args:
            oferta_id: ID da oferta
            professor_id: ID do professor

        Returns:
            Tupla (alocação criada, mensagem de erro ou None)
        """
        # Validar oferta
        try:
            oferta = self.db.query(Oferta).filter(
                Oferta.id == oferta_id
            ).first()
            if not oferta:
                return None, f"Oferta com ID {oferta_id} não encontrada"
        except Exception as e:
            return None, f"Erro ao validar oferta: {str(e)}"

        # Validar professor
        try:
            professor = self.db.query(Professor).filter(
                Professor.id == professor_id
            ).first()
            if not professor:
                return None, f"Professor com ID {professor_id} não encontrado"
        except Exception as e:
            return None, f"Erro ao validar professor: {str(e)}"

        # Verificar se oferta já possui alocação
        if self.exists_for_oferta(oferta_id):
            existing = self.get_by_oferta(oferta_id)
            return None, f"Esta oferta já possui alocação para o professor {existing.professor.nome}"

        # Validar compatibilidade de áreas (soft validation - aviso, não impedimento)
        disciplina = oferta.disciplina
        tem_competencia = any(a.id == disciplina.area.id for a in professor.areas)

        # Validar carga horária máxima
        carga_atual = float(sum(
            a.oferta.disciplina.carga_horaria
            for a in professor.alocacoes
            if a.oferta and a.oferta.disciplina
        )) if professor.alocacoes else 0.0

        carga_disciplina = float(disciplina.carga_horaria)
        carga_maxima = float(professor.carga_maxima)

        if carga_atual + carga_disciplina > carga_maxima:
            return None, (
                f"Alocação excederia a carga máxima do professor. "
                f"Atual: {carga_atual:.1f}h, Disciplina: {carga_disciplina:.1f}h, "
                f"Máximo: {carga_maxima:.1f}h"
            )

        # Criar alocação
        alocacao, error = self.create(
            oferta_id=oferta_id,
            professor_id=professor_id
        )

        if error:
            return None, error

        # Retornar aviso se não houver compatência de área
        if not tem_competencia:
            print(
                f"⚠️ Aviso: Professor {professor.nome} não possui "
                f"competência em {disciplina.area.nome} para a disciplina {disciplina.nome}"
            )

        return alocacao, None

    def delete_with_feedback(self, id: int) -> tuple[bool, Optional[str]]:
        """
        Deleta uma alocação com feedback detalhado.

        Returns:
            Tupla (sucesso, mensagem de erro ou None)
        """
        alocacao = self.get_by_id(id)
        if not alocacao:
            return False, f"Alocação com ID {id} não encontrada"

        return self.delete(id)

    def get_alocacoes_by_semestre_formatted(self, semestre_nome: str) -> List[dict]:
        """
        Retorna alocações formatadas para exportação/visualização.

        Returns:
            Lista de dicionários com dados da alocação
        """
        try:
            alocacoes = self.get_by_semestre_nome(semestre_nome)

            result = []
            for aloc in alocacoes:
                oferta = aloc.oferta
                professor = aloc.professor
                disciplina = oferta.disciplina
                semestre = oferta.semestre

                result.append({
                    "id_alocacao": aloc.id,
                    "semestre": semestre.nome,
                    "ano": semestre.ano,
                    "periodo": semestre.periodo,
                    "disciplina": disciplina.nome,
                    "turma": oferta.turma,
                    "carga_horaria": float(disciplina.carga_horaria),
                    "nivel_esperado": disciplina.nivel_esperado,
                    "area_competencia": disciplina.area.nome,
                    "professor": professor.nome,
                    "titulacao": professor.titulacao,
                    "nivel_professor": professor.nivel,
                    "modelo_contratacao": professor.modelo_contratacao,
                    "carga_maxima": float(professor.carga_maxima),
                    "status_alocacao": "Alocado"
                })

            return result
        except Exception as e:
            print(f"Erro ao formatar alocações: {str(e)}")
            return []

    def get_resumo_professor_semestre(self, professor_id: int, semestre_id: int) -> dict:
        """
        Retorna um resumo das alocações de um professor em um semestre.

        Returns:
            Dicionário com informações resumidas
        """
        try:
            alocacoes = self.db.query(Alocacao).filter(
                Alocacao.professor_id == professor_id
            ).join(
                Alocacao.oferta
            ).filter(
                Oferta.semestre_id == semestre_id
            ).all()

            carga_total = float(sum(
                a.oferta.disciplina.carga_horaria
                for a in alocacoes
                if a.oferta and a.oferta.disciplina
            )) if alocacoes else 0.0

            professor = self.db.query(Professor).filter(
                Professor.id == professor_id
            ).first()

            if not professor:
                return {}

            carga_maxima = float(professor.carga_maxima)
            carga_livre = max(0.0, carga_maxima - carga_total)
            percentual = (carga_total / carga_maxima * 100) if carga_maxima > 0 else 0.0

            return {
                "professor_id": professor_id,
                "professor_nome": professor.nome,
                "semestre_id": semestre_id,
                "carga_total": carga_total,
                "carga_maxima": carga_maxima,
                "carga_livre": carga_livre,
                "percentual_utilizado": percentual,
                "total_disciplinas": len(alocacoes)
            }
        except Exception as e:
            print(f"Erro ao gerar resumo: {str(e)}")
            return {}

    def get_resumo_oferta_semestre(self, semestre_id: int) -> dict:
        """
        Retorna um resumo das alocações de um semestre.

        Returns:
            Dicionário com estatísticas
        """
        try:
            ofertas_totais = self.db.query(Oferta).filter(
                Oferta.semestre_id == semestre_id
            ).count()

            ofertas_alocadas = self.db.query(Oferta).filter(
                Oferta.semestre_id == semestre_id
            ).join(
                Oferta.alocacoes
            ).count()

            ofertas_pendentes = ofertas_totais - ofertas_alocadas

            return {
                "semestre_id": semestre_id,
                "ofertas_totais": ofertas_totais,
                "ofertas_alocadas": ofertas_alocadas,
                "ofertas_pendentes": ofertas_pendentes,
                "percentual_alocacao": (ofertas_alocadas / ofertas_totais * 100) if ofertas_totais > 0 else 0.0
            }
        except Exception as e:
            print(f"Erro ao gerar resumo de ofertas: {str(e)}")
            return {}

    def bulk_create(self, alocacoes_data: List[dict]) -> tuple[List[Alocacao], List[str]]:
        """
        Cria múltiplas alocações em lote.

        Args:
            alocacoes_data: Lista de dicts com 'oferta_id' e 'professor_id'

        Returns:
            Tupla (lista de alocações criadas, lista de erros)
        """
        alocacoes_criadas = []
        erros = []

        for idx, data in enumerate(alocacoes_data):
            oferta_id = data.get('oferta_id')
            professor_id = data.get('professor_id')

            if not oferta_id or not professor_id:
                erros.append(f"Item {idx}: oferta_id e professor_id são obrigatórios")
                continue

            alocacao, error = self.create_with_validation(oferta_id, professor_id)
            if error:
                erros.append(f"Item {idx}: {error}")
            else:
                alocacoes_criadas.append(alocacao)

        return alocacoes_criadas, erros

