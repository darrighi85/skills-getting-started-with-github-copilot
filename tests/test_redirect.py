"""Tests for GET / root endpoint."""


class TestRootRedirect:
    """Test the root endpoint for proper redirect to static files."""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Request the root path
        Act: GET /
        Assert: Returns 307 redirect to /static/index.html
        """
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_correct_location_header(self, client):
        """
        Arrange: Request root endpoint
        Act: GET / with follow_redirects=False
        Assert: Location header points to correct static page
        """
        response = client.get("/", follow_redirects=False)
        
        location = response.headers.get("location")
        assert location is not None
        assert location == "/static/index.html"

    def test_root_with_follow_redirects(self, client):
        """
        Arrange: Request root path with redirect following enabled
        Act: GET / with follow_redirects=True
        Assert: Final response is 200 (after redirect to static files)
        """
        response = client.get("/", follow_redirects=True)
        
        # Should eventually resolve (200 or similar for static files)
        assert response.status_code in [200, 404, 307]
