"""
Service for fetching papers from arXiv API.
"""
import arxiv
from typing import List
from app.models.schemas import Paper


def fetch_arxiv_papers(query: str, max_results: int = 10) -> List[Paper]:
    """
    Fetch relevant papers from arXiv based on a query.

    Args:
        query: Search query string
        max_results: Maximum number of papers to return

    Returns:
        List of Paper objects
    """
    client = arxiv.Client()

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    papers = []
    for result in client.results(search):
        paper = Paper(
            id=result.entry_id.split("/")[-1],
            title=result.title,
            authors=[str(author) for author in result.authors],
            summary=result.summary,
            published=result.published.isoformat(),
            pdf_url=result.pdf_url,
            primary_category=result.primary_category
        )
        papers.append(paper)

    return papers
