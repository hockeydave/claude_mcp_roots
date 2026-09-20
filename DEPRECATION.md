The "Roots" feature in Anthropic's Model Context Protocol (MCP) is deprecated.
The feature was officially deprecated as of the July 28, 2026 specification update (MCP v2 / SEP-2577).

## Why was it deprecated?

Roots originally allowed clients to advertise relevant filesystem directories or boundaries to servers. However, the core protocol maintainers noted that it was a very niche feature with confusing semantics. Furthermore, it was only informational and did not provide strict access control or security containment by itself.

The deprecation came alongside a massive architectural rewrite that made MCP entirely stateless (removing protocol-level sessions and initialization handshakes) to allow servers to scale cleanly behind standard load balancers. Two other original stateful primitives—Sampling and Logging—were deprecated in the same release.

## What is the timeline and replacement?
* The 12-Month Rule: Under MCP's feature lifecycle policy, deprecated features remain fully functional for a minimum transition window of 12 months from the deprecation date before they can be completely removed from the spec.
* The Replacement: For new implementations, developers are advised against adopting Roots. Instead, you should migrate to passing specific files or directories explicitly via tool parameters, resource URIs, or server configurations.

If you are migrating an existing server, look out for MCPDeprecationWarning flags in the SDK when calling legacy client methods like session.list_roots().