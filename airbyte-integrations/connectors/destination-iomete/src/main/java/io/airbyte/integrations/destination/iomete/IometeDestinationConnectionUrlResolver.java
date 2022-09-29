/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iomete;

import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * IometeConnectionUrlConfig contains helpers to resolve connection url object from configuration.
 * If user provided the connection url incorrect, it will send to dummy url to disconnect.
 */
class IometeDestinationConnectionUrlResolver {

    private static final Logger LOGGER = LoggerFactory.getLogger(IometeDestinationConnectionUrlResolver.class);

    public String lakehouseHostname;
    public String accountNumber;
    public String lakehouseName;

    public IometeDestinationConnectionUrlResolver() {
        this.lakehouseHostname = IometeConstants.LAKEHOUSE_HOSTNAME_EXAMPLE;
        this.accountNumber = IometeConstants.ACCOUNT_NUMBER_EXAMPLE;
        this.lakehouseName = IometeConstants.DEFAULT_LAKEHOUSE_NAME;
    }

    public IometeDestinationConnectionUrlResolver(String lakehouseHostname,
                                                  String accountNumber,
                                                  String lakehouseName) {
        this.lakehouseHostname = lakehouseHostname;
        this.accountNumber = accountNumber;
        this.lakehouseName = lakehouseName;
    }

    public static IometeDestinationConnectionUrlResolver create(String connectionUrl) {
        String withoutProtocol = StringUtils.substringAfter(connectionUrl, IometeConstants.AIRBYTE_PROTOCOL);
        String[] params = StringUtils.strip(withoutProtocol, "/").split("/");
        if (params.length != 3) {
            LOGGER.warn("Connection string is incorrect =" + connectionUrl);
            return new IometeDestinationConnectionUrlResolver();
        }
        return new IometeDestinationConnectionUrlResolver(params[0], params[1], params[2]);
    }

}
