/**
 * lib/api.js — the fetch wrapper. Every other module (and test) mocks the
 * exported functions, so this is the only place the raw HTTP behavior is
 * pinned: error normalization (the `Error.message` contract the UI and
 * RenameButton's 409 parsing depend on) and URL encoding.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import * as api from "./api.js";

/** A minimal `Response` stand-in (only the members api.js touches). */
function res(status, body, statusText = "") {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText,
    json: async () => body,
  };
}

const fetchMock = vi.fn();
beforeEach(() => {
  fetchMock.mockReset();
  globalThis.fetch = fetchMock;
});

describe("success paths", () => {
  it("returns the parsed JSON body", async () => {
    fetchMock.mockResolvedValue(res(200, { files: [] }));
    await expect(api.listFiles("/x")).resolves.toEqual({ files: [] });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/list?path=%2Fx",
      expect.objectContaining({ method: "GET" })
    );
  });

  it("URL-encodes the path (spaces, unicode)", async () => {
    fetchMock.mockResolvedValue(res(200, { files: [] }));
    await api.listFiles("/a b");
    expect(fetchMock.mock.calls[0][0]).toBe("/api/list?path=%2Fa%20b");
  });

  it("sends a JSON body with Content-Type on POST, none on GET", async () => {
    fetchMock.mockResolvedValue(res(200, { path: "", previews: {} }));
    await api.preview({ path: "/x", files: ["a.txt"], dirs: [], config: {} });
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/preview");
    expect(init.method).toBe("POST");
    expect(init.headers["Content-Type"]).toBe("application/json");
    expect(JSON.parse(init.body)).toEqual({ path: "/x", files: ["a.txt"], dirs: [], config: {} });
  });

  it("GET requests carry no body and no Content-Type", async () => {
    fetchMock.mockResolvedValue(res(200, { path: "/x", files: [] }));
    await api.listFiles("/x");
    const [, init] = fetchMock.mock.calls[0];
    expect(init.body).toBeUndefined();
    expect(init.headers).toBeUndefined();
  });

  it("returns null for 204", async () => {
    fetchMock.mockResolvedValue(res(204, null));
    await expect(api.rename({})).resolves.toBeNull();
  });

  it("homeDir hits /api/home (no query)", async () => {
    fetchMock.mockResolvedValue(res(200, { path: "/home" }));
    await expect(api.homeDir()).resolves.toEqual({ path: "/home" });
    expect(fetchMock.mock.calls[0][0]).toBe("/api/home");
  });
});

describe("error normalization", () => {
  it("uses the backend's string detail as the message (e.g. friendly 403)", async () => {
    fetchMock.mockResolvedValue(res(403, { detail: "Permission denied" }, "Forbidden"));
    await expect(api.listFiles("/x")).rejects.toThrow("Permission denied");
  });

  it("stringifies an object detail — the 409 body RenameButton parses back", async () => {
    const detail = { duplicates: 2, names: ["a.txt", "b.log"] };
    fetchMock.mockResolvedValue(res(409, { detail }, "Conflict"));
    await api
      .rename({})
      .catch((e) => {
        // api.js: non-string details become JSON.stringify(detail), so
        // RenameButton.dupeNamesFromError(e) can JSON.parse(e.message).
        expect(e.message).toBe(JSON.stringify(detail));
        expect(JSON.parse(e.message)).toEqual(detail);
      });
  });

  it("falls back to status text for non-JSON error bodies", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      json: async () => {
        throw new Error("not json");
      },
    });
    await expect(api.preview({})).rejects.toThrow("500 Internal Server Error");
  });

  it("propagates network failures as-is", async () => {
    fetchMock.mockRejectedValue(new TypeError("Failed to fetch"));
    await expect(api.listFiles("/x")).rejects.toThrow("Failed to fetch");
  });
});