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
    try:
        print(f"🔍 arXiv Service: Searching for papers with query: {query}")
        
        client = arxiv.Client(
            page_size=100,
            delay_seconds=3,
            num_retries=3
        )

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        papers = []
        for i, result in enumerate(client.results(search)):
            try:
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
                print(f"📄 arXiv Service: Fetched paper {i+1}: {paper.title[:50]}...")
                
            except Exception as e:
                print(f"⚠️ arXiv Service: Error processing paper {i}: {str(e)}")
                continue

        print(f"✅ arXiv Service: Successfully fetched {len(papers)} papers")
        return papers

    except arxiv.HTTPError as e:
        print(f"❌ arXiv Service: HTTP Error {e.status}: {str(e)}")
        print(f"   Query was: {query}")
        # Try with a simpler query if the original was too complex
        if len(query) > 200 or query.count('(') > 3:
            simple_query = query.split(' AND ')[0].strip('()"')
            print(f"🔄 arXiv Service: Retrying with simpler query: {simple_query}")
            return fetch_arxiv_papers(simple_query, max_results)
        return []
        
    except Exception as e:
        print(f"❌ arXiv Service: Unexpected error: {str(e)}")
        return []
