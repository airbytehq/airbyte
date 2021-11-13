using Airbyte.Cdk.Models;

namespace Airbyte.Cdk.Sources.Utils
{
    public static class CatalogHelper
    {
        /// <summary>
        /// Updates the sync mode on all streams in this catalog to be full refresh
        /// </summary>
        /// <param name="catalog"></param>
        /// <returns></returns>
        public static AirbyteCatalog CoerceAirbyteCatalogAsFullRefresh(AirbyteCatalog catalog)
        {
            var coercedCatalog = new AirbyteCatalog { Streams = catalog.Streams };
            foreach (var stream in coercedCatalog.Streams)
            {
                stream.SourceDefinedCursor = false;
                stream.SupportedSyncModes = new[] { SyncMode.full_refresh };
                stream.DefaultCursorField = null;
            }

            return coercedCatalog;
        }
    }
}
