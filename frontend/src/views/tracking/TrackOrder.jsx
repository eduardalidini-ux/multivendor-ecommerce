import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import useAxios from '../../utils/useAxios'

function TrackOrder() {
    const axios = useAxios()
    const param = useParams()

    const [payload, setPayload] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true)
            try {
                const res = await axios.get(`warehouse/track/order/${param.orderOid}/`)
                setPayload(res.data)
            } catch (e) {
                setPayload(null)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [param.orderOid])

    const order = payload?.order
    const shipment = payload?.shipment

    const externalTracks = (order?.orderitem || []).map((i) => {
        const url = i?.delivery_couriers?.tracking_website
        const urlParam = i?.delivery_couriers?.url_parameter
        const id = i?.tracking_id
        if (!url || !urlParam || !id) return null
        return {
            orderItemId: i.id,
            productTitle: i?.product?.title,
            trackingUrl: `${url}?${urlParam}=${encodeURIComponent(id)}`,
            trackingId: id,
            courierName: i?.delivery_couriers?.name,
        }
    }).filter(Boolean)

    return (
        <div className='container mt-5' style={{ marginBottom: 150 }}>
            <div className='d-flex align-items-center justify-content-between mb-3'>
                <h3 className='mb-0'>Order Tracking</h3>
                <Link className='btn btn-outline-secondary' to='/'>Home</Link>
            </div>

            {loading && <div className='text-center'>Loading...</div>}

            {!loading && !payload && (
                <div className='alert alert-danger'>Order not found or you do not have access.</div>
            )}

            {!loading && payload && (
                <>
                    <div className='rounded shadow p-3 bg-white mb-4'>
                        <div className='d-flex align-items-center justify-content-between'>
                            <h5 className='mb-0'>Order #{order?.oid}</h5>
                            <div>
                                <span className='badge bg-secondary me-2'>{String(order?.payment_status || '').toUpperCase()}</span>
                                <span className='badge bg-primary'>{order?.order_status}</span>
                            </div>
                        </div>
                        <hr />
                        <div className='row'>
                            <div className='col-lg-6'>
                                <h6>Customer</h6>
                                <div className='fw-bold'>{order?.full_name}</div>
                                <div className='text-muted'>{order?.email}</div>
                                <div className='text-muted'>{order?.mobile}</div>
                            </div>
                            <div className='col-lg-6'>
                                <h6>Shipping Address</h6>
                                <div>{order?.address}</div>
                                <div className='text-muted'>{[order?.city, order?.state, order?.country].filter(Boolean).join(', ')}</div>
                            </div>
                        </div>
                    </div>

                    <div className='rounded shadow p-3 bg-white mb-4'>
                        <div className='d-flex align-items-center justify-content-between'>
                            <h5 className='mb-0'>Shipment</h5>
                            {!shipment && (
                                <span className='badge bg-warning text-dark'>Not assigned yet</span>
                            )}
                            {shipment && (
                                <span className='badge bg-success'>{shipment.status}</span>
                            )}
                        </div>
                        <hr />
                        {shipment && (
                            <div className='text-muted'>
                                Courier: {shipment.courier?.full_name || shipment.courier?.email || '—'}
                            </div>
                        )}
                    </div>

                    <div className='rounded shadow p-3 bg-white'>
                        <h5 className='mb-3'>Timeline</h5>
                        {!shipment && (
                            <div className='text-muted'>No shipment events yet.</div>
                        )}
                        {shipment && (
                            <ul className='list-group'>
                                {(shipment.events || []).map((e) => (
                                    <li key={e.id} className='list-group-item d-flex justify-content-between align-items-start'>
                                        <div>
                                            <div className='fw-bold'>{e.event_type}</div>
                                            {e.message && <div className='text-muted'>{e.message}</div>}
                                        </div>
                                        <div className='text-muted' style={{ fontSize: 12 }}>{new Date(e.created_at).toLocaleString()}</div>
                                    </li>
                                ))}
                                {(!shipment.events || shipment.events.length === 0) && (
                                    <li className='list-group-item text-muted'>No events yet.</li>
                                )}
                            </ul>
                        )}
                    </div>

                    <div className='rounded shadow p-3 bg-white mt-4'>
                        <h5 className='mb-3'>Order Items</h5>
                        <table className='table align-middle mb-0 bg-white'>
                            <thead className='bg-light'>
                                <tr>
                                    <th>Product</th>
                                    <th>Price</th>
                                    <th>Qty</th>
                                    <th>Total</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {(order?.orderitem || []).map((item) => (
                                    <tr key={item.id}>
                                        <td>
                                            <div className='d-flex align-items-center'>
                                                {item?.product?.image && (
                                                    <img
                                                        src={item.product.image}
                                                        style={{ width: 60, height: 60, objectFit: 'cover', borderRadius: 10 }}
                                                        alt=''
                                                    />
                                                )}
                                                <div className='ms-2'>
                                                    <div className='fw-bold'>{item?.product?.title}</div>
                                                    <div className='text-muted' style={{ fontSize: 12 }}>#{item.oid}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>${item?.product?.price}</td>
                                        <td>{item.qty}</td>
                                        <td>${item.sub_total}</td>
                                        <td>{item.delivery_status}</td>
                                    </tr>
                                ))}
                                {(!order?.orderitem || order.orderitem.length === 0) && (
                                    <tr>
                                        <td colSpan={5} className='text-center text-muted'>No order items.</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>

                    {externalTracks.length > 0 && (
                        <div className='rounded shadow p-3 bg-white mt-4'>
                            <h5 className='mb-3'>External Tracking (Vendor Provided)</h5>
                            <table className='table align-middle mb-0 bg-white'>
                                <thead className='bg-light'>
                                    <tr>
                                        <th>Item</th>
                                        <th>Courier</th>
                                        <th>Tracking ID</th>
                                        <th>Link</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {externalTracks.map((t) => (
                                        <tr key={t.orderItemId}>
                                            <td>{t.productTitle}</td>
                                            <td>{t.courierName || '—'}</td>
                                            <td>{t.trackingId}</td>
                                            <td>
                                                <a className='btn btn-sm btn-outline-secondary' href={t.trackingUrl} target='_blank' rel='noreferrer'>Open</a>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                    <div className='mt-4'>
                        <Link className='btn btn-outline-primary' to='/customer/orders/'>Back to Orders</Link>
                    </div>
                </>
            )}
        </div>
    )
}

export default TrackOrder
