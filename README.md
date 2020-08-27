<p align="center">
  <a href="https://dataline.io">
    <img src="https://dataline.io/wp-content/uploads/2020/08/Dataline_light-background.svg" width="318px" alt="Dataline logo" />
  </a>
</p>
<h3 align="center">Data integration made simple, secure and reliable</h3>
<p align="center">The new open-source standard to sync data from applications & databases to warehouses.</p>
<br />

<p align="center">
  <a href="https://docs.dataline.io/deployment/deploying-dataline">
    <img src="https://dataline.io/wp-content/uploads/2020/08/Deploy-with-Docker.png"  />
  </a>
</p>

<br>

<p align="center">
  <a href="https://dataline.io">
    <img src="https://dataline.io/wp-content/uploads/2020/08/Sources_List.png" alt="Sources panel" />
  </a>
</p>

<br>

Dataline is on a mission to make data integration pipelines a commodity.

- **Maintenance-free connectors you can use in minutes**. Just authenticate your sources and warehouse, and get connectors that adapts to schema and API changes for you.
- On a mission to **cover the long tail of integrations**, as Dataline will be very active in maintaining the pipelines’ reliability. 
- **Building new integrations made trivial**. We make it very easy to add new integrations that you need, by offering scheduling and orchestration. 
- **Your data stays in your cloud**. Have full control over your data, and the costs of your data transfers. 
- **No more security compliance process** to go through as self-hosted. 
- **No more pricing indexed on volume**, as cloud-based solutions offer. 

# Getting Started

## Quick start

```bash
docker-compose up
```

Now go to [http://localhost:8000](http://localhost:8000)

## Update images

```bash
docker-compose -f docker-compose.build.yaml build
docker-compose -f docker-compose.build.yaml push
```

