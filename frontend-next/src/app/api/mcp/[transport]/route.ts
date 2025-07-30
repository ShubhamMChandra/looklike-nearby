import { createMcpHandler, withMcpAuth } from 'mcp-handler';
import { z } from 'zod';
import { AuthInfo } from '@modelcontextprotocol/sdk/server/auth/types.js';
import { api } from '@/lib/api';

const handler = createMcpHandler(
  (server) => {
    // Search for similar businesses
    server.tool(
      'search_similar_businesses',
      'Search for businesses similar to a reference client within a specified radius',
      {
        reference_client_id: z.number().optional(),
        custom_address: z.string().optional(),
        radius_meters: z.number().min(1000).max(50000),
        business_type: z.string().optional(),
      },
      async ({ reference_client_id, custom_address, radius_meters, business_type }) => {
        const response = await api.searchProspects({
          reference_client_id,
          custom_address,
          radius_meters,
          filters: business_type ? { business_type } : undefined,
        });

        if (response.error) {
          throw new Error(response.error.message);
        }

        const prospects = response.data || [];
        return {
          content: [
            {
              type: 'text',
              text: `Found ${prospects.length} similar businesses:\n\n` +
                prospects.map(p => `- ${p.name} (${p.address})`).join('\n'),
            },
          ],
        };
      }
    );

    // Add reference client
    server.tool(
      'add_reference_client',
      'Add a new reference client to the system',
      {
        name: z.string(),
        address: z.string(),
        business_type: z.string().optional(),
        notes: z.string().optional(),
      },
      async ({ name, address, business_type, notes }) => {
        const response = await api.createReferenceClient({
          name,
          address,
          business_type,
          notes,
        });

        if (response.error) {
          throw new Error(response.error.message);
        }

        const client = response.data;
        if (!client) {
          throw new Error('Failed to create reference client');
        }
        return {
          content: [
            {
              type: 'text',
              text: `✅ Added reference client: ${client.name}\nAddress: ${client.address}${
                business_type ? `\nType: ${business_type}` : ''
              }${notes ? `\nNotes: ${notes}` : ''}`,
            },
          ],
        };
      }
    );

    // Create campaign
    server.tool(
      'create_campaign',
      'Create a new sales campaign',
      {
        name: z.string(),
        description: z.string().optional(),
      },
      async ({ name, description }) => {
        const response = await api.createCampaign({
          name,
          description,
        });

        if (response.error) {
          throw new Error(response.error.message);
        }

        const campaign = response.data;
        if (!campaign) {
          throw new Error('Failed to create campaign');
        }
        return {
          content: [
            {
              type: 'text',
              text: `✅ Created campaign: ${campaign.name}${
                description ? `\nDescription: ${description}` : ''
              }`,
            },
          ],
        };
      }
    );

    // Add prospect to campaign
    server.tool(
      'add_prospect_to_campaign',
      'Add a prospect to a campaign with status',
      {
        campaign_id: z.number(),
        prospect_id: z.number(),
        status: z.enum(['NEW', 'CONTACTED', 'QUALIFIED', 'NOT_INTERESTED', 'CONVERTED']),
        notes: z.string().optional(),
      },
      async ({ campaign_id, prospect_id, status, notes }) => {
        const response = await api.addProspectToCampaign(campaign_id, prospect_id, {
          status,
          notes,
        });

        if (response.error) {
          throw new Error(response.error.message);
        }

        return {
          content: [
            {
              type: 'text',
              text: `✅ Added prospect ${prospect_id} to campaign ${campaign_id} with status: ${status}${
                notes ? `\nNotes: ${notes}` : ''
              }`,
            },
          ],
        };
      }
    );
  },
  {},
  {}
);

// Simple token verification for demo
const verifyToken = async (
  req: Request,
  bearerToken?: string,
): Promise<AuthInfo | undefined> => {
  if (!bearerToken) return undefined;

  // In production, you should verify the token properly
  // For now, we'll accept any token that starts with "sk-"
  const isValid = bearerToken.startsWith('sk-');
  if (!isValid) return undefined;

  return {
    token: bearerToken,
    scopes: ['read:prospects', 'write:prospects'],
    clientId: 'demo-client',
    extra: {
      userId: 'demo-user',
    },
  };
};

// Add authentication
const authHandler = withMcpAuth(handler, verifyToken, {
  required: true,
  requiredScopes: ['read:prospects'],
  resourceMetadataPath: '/.well-known/oauth-protected-resource',
});

export { authHandler as GET, authHandler as POST };