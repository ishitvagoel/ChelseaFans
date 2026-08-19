import { describe, expect, it } from "vitest";

import { formatNumber } from "./utils";

describe("formatNumber", () => {
  it("renders em dash for missing stats so zeros are not invented", () => {
    expect(formatNumber(null)).toBe("—");
    expect(formatNumber(undefined)).toBe("—");
  });

  it("keeps explicit zeros", () => {
    expect(formatNumber(0)).toBe("0");
  });
});
