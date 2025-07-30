import {
  protectedResourceHandler,
  metadataCorsOptionsRequestHandler,
} from 'mcp-handler';

const handler = protectedResourceHandler({
  authServerUrls: ['https://looklike-nearby-production.up.railway.app'],
  availableScopes: {
    'read:prospects': 'Read access to prospects and reference clients',
    'write:prospects': 'Write access to prospects and campaigns',
  },
  documentationUrl: 'https://github.com/ShubhamMChandra/looklike-nearby#readme',
});

export { handler as GET, metadataCorsOptionsRequestHandler as OPTIONS };