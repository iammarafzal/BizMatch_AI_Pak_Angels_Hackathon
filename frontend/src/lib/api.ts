/**
 * BizMatch AI - Production Typed API Client
 * Connects directly and strictly to the running FastAPI backend.
 * Zero dummy data or client-side mock generators.
 */

import {
  Business,
  BusinessCreate,
  Manager,
  BatchMatchResponse,
  AnalyzeRequirementsRequest,
  StructuredRequirements,
  CalculateMatchesRequest,
  ExplainMatchRequest,
  ExplainMatchResponse,
  DemoPresetResponse,
} from "@/types/api";

const RAW_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const BASE_URL = RAW_BASE.replace(/\/+$/, "");
export const API_BASE = BASE_URL.endsWith("/api") ? BASE_URL : `${BASE_URL}/api`;

export class ApiError extends Error {
  status: number;
  details?: string[] | string | unknown;

  constructor(message: string, status: number, details?: string[] | string | unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

let cachedToken: string | null = null;

/**
 * Automatically acquires and caches a JWT bearer token using demo credentials
 * for protected core backend routes.
 */
async function getAuthToken(): Promise<string | null> {
  if (cachedToken) return cachedToken;
  if (typeof window !== "undefined") {
    const stored = sessionStorage.getItem("bizmatch_jwt_token");
    if (stored) {
      cachedToken = stored;
      return stored;
    }
  }

  try {
    const loginUrl = `${API_BASE}/auth/login`;
    const res = await fetch(loginUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: "founder@bizmatch.ai",
        password: "password123",
      }),
    });
    if (res.ok) {
      const data = await res.json();
      const token = data.access_token || data.token;
      if (token) {
        cachedToken = token;
        if (typeof window !== "undefined") {
          sessionStorage.setItem("bizmatch_jwt_token", token);
        }
        return token;
      }
    }
  } catch (err) {
    console.warn("Could not acquire auth token automatically:", err);
  }
  return null;
}

/**
 * Universal typed request executor with unified FastAPI error handling:
 * - 422 Unprocessable Entity formatting
 * - 401 Unauthorized token refresh & single retry
 * - 500 Internal Server Error human-readable messages
 */
async function request<T>(endpoint: string, options: RequestInit = {}, retryCount = 0): Promise<T> {
  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;

  const token = await getAuthToken();

  const defaultHeaders: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    defaultHeaders["Authorization"] = `Bearer ${token}`;
  }

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (response.status === 401 && retryCount === 0) {
      // Clear expired token and retry once
      cachedToken = null;
      if (typeof window !== "undefined") {
        sessionStorage.removeItem("bizmatch_jwt_token");
      }
      await getAuthToken();
      return request<T>(endpoint, options, 1);
    }

    let payload: unknown;
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      payload = await response.json();
    } else {
      payload = await response.text();
    }

    if (!response.ok) {
      let formattedMsg = `HTTP Request failed with status ${response.status}`;
      let errorDetails: unknown = null;

      if (typeof payload === "object" && payload !== null) {
        const errObj = payload as Record<string, unknown>;

        // FastAPI 422 Unprocessable Entity array parsing
        if (response.status === 422 && Array.isArray(errObj.details)) {
          formattedMsg = `Validation Error: ${(errObj.details as string[]).join("; ")}`;
          errorDetails = errObj.details;
        } else if (response.status === 422 && Array.isArray(errObj.detail)) {
          const detailList = (errObj.detail as Array<{ loc?: string[]; msg?: string }>).map(
            (d) => `${d.loc ? d.loc.join(" -> ") : "field"}: ${d.msg || "invalid"}`
          );
          formattedMsg = `Validation Error: ${detailList.join("; ")}`;
          errorDetails = detailList;
        } else {
          formattedMsg =
            String(errObj.error || errObj.detail || errObj.message || formattedMsg);
          errorDetails = errObj.details || errObj.detail;
        }
      }

      throw new ApiError(formattedMsg, response.status, errorDetails);
    }

    return payload as T;
  } catch (error: unknown) {
    if (error instanceof ApiError) {
      throw error;
    }
    const errMessage =
      error instanceof Error ? error.message : "Network error connecting to BizMatch AI backend service";
    throw new ApiError(errMessage, 500, error);
  }
}

/**
 * 1. Fetch FashionCart demo preset firmographics ($2,000/mo budget)
 * Endpoint: GET /api/demo/fashioncart
 */
export async function getFashionCartDemoData(): Promise<Business> {
  const res = await request<DemoPresetResponse | Business>("/demo/fashioncart");
  if ("data" in res && res.data) {
    return res.data;
  }
  return res as Business;
}

/**
 * 2. Parse unstructured founder goals & challenges into structured requirements
 * Endpoint: POST /api/analyze-requirements
 */
export async function analyzeRequirements(
  payload: AnalyzeRequirementsRequest
): Promise<StructuredRequirements> {
  const res = await request<StructuredRequirements | { success: boolean; data: StructuredRequirements }>(
    "/analyze-requirements",
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
  if ("data" in res && res.data) {
    return res.data;
  }
  return res as StructuredRequirements;
}

/**
 * 3. Compute 6-factor deterministic compatibility matches for a business
 * Endpoint: POST /api/matches/calculate
 */
export async function calculateMatches(
  businessData: CalculateMatchesRequest | string
): Promise<BatchMatchResponse> {
  let body: CalculateMatchesRequest;

  if (typeof businessData === "string") {
    body = { business_id: businessData };
  } else if (businessData.business_data) {
    body = { business_data: businessData.business_data };
  } else {
    body = { business_id: businessData.business_id || "biz-fashioncart" };
  }

  return request<BatchMatchResponse>("/matches/calculate?include_explanations=true", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/**
 * 4. Generate explainable decision support card for candidate
 * Endpoint: POST /api/matches/explain
 */
export async function getMatchExplanation(
  businessId: string | number,
  managerId: string | number,
  customContext?: Record<string, unknown>
): Promise<ExplainMatchResponse> {
  const payload: ExplainMatchRequest = {
    business_id: businessId,
    manager_id: managerId,
    custom_business_context: customContext,
  };

  return request<ExplainMatchResponse>("/matches/explain", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** Alias for getMatchExplanation */
export const getCandidateExplanation = getMatchExplanation;

/**
 * 5. Fetch curated manager pool from backend
 * Endpoint: GET /api/managers
 */
export async function getManagers(limit: number = 20): Promise<Manager[]> {
  return request<Manager[]>(`/managers?limit=${limit}`);
}

/**
 * 6. Fetch single manager candidate by ID
 * Endpoint: GET /api/managers/{id}
 */
export async function getManagerById(managerId: string): Promise<Manager> {
  return request<Manager>(`/managers/${managerId}`);
}

/**
 * 7. Fetch business profiles
 * Endpoint: GET /api/businesses
 */
export async function getBusinesses(): Promise<Business[]> {
  return request<Business[]>("/businesses");
}

/**
 * 8. Fetch single business profile by ID
 * Endpoint: GET /api/businesses/{id}
 */
export async function getBusinessById(businessId: string): Promise<Business> {
  return request<Business>(`/businesses/${businessId}`);
}

/**
 * 9. Create a new business profile
 * Endpoint: POST /api/businesses
 */
export async function createBusiness(payload: BusinessCreate): Promise<Business> {
  return request<Business>("/businesses", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
